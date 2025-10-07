from pymongo import MongoClient
from datetime import datetime
import hashlib
import config
import ssl

client = MongoClient(
    config.MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=10000
)
db = client.telegram_bots

users_collection = db.users
videos_collection = db.videos
settings_collection = db.settings
stats_collection = db.stats
referrals_collection = db.referrals
analytics_collection = db.analytics

def generate_video_id(file_id):
    hash_object = hashlib.md5(f"{file_id}{datetime.now()}".encode())
    return hash_object.hexdigest()[:12]

def add_user(user_id, username=None, bot_number=1, referred_by=None):
    existing_user = users_collection.find_one({"user_id": user_id, "bot_number": bot_number})
    
    user_data = {
        "user_id": user_id,
        "username": username,
        "bot_number": bot_number,
        "joined_date": datetime.now(),
        "is_banned": False,
        "language": "en",
        "total_videos_watched": 0,
        "last_active": datetime.now(),
        "referred_by": referred_by,
        "referral_count": 0,
        "referral_points": 0
    }
    
    if not existing_user:
        users_collection.insert_one(user_data)
        if referred_by:
            users_collection.update_one(
                {"user_id": referred_by, "bot_number": bot_number},
                {
                    "$inc": {"referral_count": 1, "referral_points": 10},
                    "$set": {"last_active": datetime.now()}
                }
            )
            referrals_collection.insert_one({
                "referrer_id": referred_by,
                "referred_id": user_id,
                "bot_number": bot_number,
                "date": datetime.now()
            })
    else:
        users_collection.update_one(
            {"user_id": user_id, "bot_number": bot_number},
            {"$set": {"last_active": datetime.now()}}
        )

def get_user(user_id, bot_number=1):
    return users_collection.find_one({"user_id": user_id, "bot_number": bot_number})

def update_user_language(user_id, bot_number, language):
    users_collection.update_one(
        {"user_id": user_id, "bot_number": bot_number},
        {"$set": {"language": language, "last_active": datetime.now()}}
    )

def ban_user(user_id, bot_number=1):
    users_collection.update_one(
        {"user_id": user_id, "bot_number": bot_number},
        {"$set": {"is_banned": True}}
    )

def unban_user(user_id, bot_number=1):
    users_collection.update_one(
        {"user_id": user_id, "bot_number": bot_number},
        {"$set": {"is_banned": False}}
    )

def store_video(file_id, file_unique_id, message_id, bot_number=1, caption=None, thumbnail=None):
    video_id = generate_video_id(file_id)
    video_data = {
        "video_id": video_id,
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "message_id": message_id,
        "bot_number": bot_number,
        "posted_date": datetime.now(),
        "views": 0,
        "unique_viewers": [],
        "caption": caption,
        "thumbnail": thumbnail,
        "engagement_score": 0
    }
    videos_collection.insert_one(video_data)
    return video_id

def get_video(video_id):
    return videos_collection.find_one({"video_id": video_id})

def increment_video_views(video_id, user_id=None):
    update_data = {"$inc": {"views": 1}}
    if user_id:
        video = get_video(video_id)
        if video and user_id not in video.get("unique_viewers", []):
            update_data["$push"] = {"unique_viewers": user_id}
            update_data["$inc"]["engagement_score"] = 5
    
    videos_collection.update_one({"video_id": video_id}, update_data)
    
    if user_id:
        users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"total_videos_watched": 1}, "$set": {"last_active": datetime.now()}}
        )

def get_total_users(bot_number=None):
    if bot_number:
        return users_collection.count_documents({"bot_number": bot_number})
    return users_collection.count_documents({})

def get_total_videos(bot_number=None):
    if bot_number:
        return videos_collection.count_documents({"bot_number": bot_number})
    return videos_collection.count_documents({})

def get_all_user_ids(bot_number=1):
    users = users_collection.find({"bot_number": bot_number, "is_banned": False})
    return [user["user_id"] for user in users]

def get_active_users_today(bot_number=1):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return users_collection.count_documents({
        "bot_number": bot_number,
        "last_active": {"$gte": today_start}
    })

def get_top_referrers(bot_number=1, limit=10):
    return list(users_collection.find(
        {"bot_number": bot_number, "referral_count": {"$gt": 0}}
    ).sort("referral_points", -1).limit(limit))

def get_trending_videos(bot_number=1, limit=10):
    return list(videos_collection.find(
        {"bot_number": bot_number}
    ).sort("engagement_score", -1).limit(limit))

def set_required_channels(bot_number, channels):
    settings_collection.update_one(
        {"bot_number": bot_number, "setting_name": "required_channels"},
        {"$set": {"channels": channels, "updated_at": datetime.now()}},
        upsert=True
    )

def get_required_channels(bot_number):
    setting = settings_collection.find_one({"bot_number": bot_number, "setting_name": "required_channels"})
    if setting:
        return setting.get("channels", [])
    return config.BOT_REQUIRED_CHANNELS.get(bot_number, [])

def update_stats(stat_type, value=1):
    stats_collection.update_one(
        {"stat_type": stat_type},
        {"$inc": {"value": value}, "$set": {"last_updated": datetime.now()}},
        upsert=True
    )

def get_stat(stat_type):
    stat = stats_collection.find_one({"stat_type": stat_type})
    if stat:
        return stat.get("value", 0)
    return 0

def log_analytics_event(bot_number, event_type, user_id=None, metadata=None):
    analytics_collection.insert_one({
        "bot_number": bot_number,
        "event_type": event_type,
        "user_id": user_id,
        "metadata": metadata,
        "timestamp": datetime.now()
    })

def get_analytics_summary(bot_number, days=7):
    from datetime import timedelta
    start_date = datetime.now() - timedelta(days=days)
    
    events = list(analytics_collection.find({
        "bot_number": bot_number,
        "timestamp": {"$gte": start_date}
    }))
    
    summary = {
        "total_events": len(events),
        "unique_users": len(set(e.get("user_id") for e in events if e.get("user_id"))),
        "events_by_type": {}
    }
    
    for event in events:
        event_type = event.get("event_type", "unknown")
        summary["events_by_type"][event_type] = summary["events_by_type"].get(event_type, 0) + 1
    
    return summary

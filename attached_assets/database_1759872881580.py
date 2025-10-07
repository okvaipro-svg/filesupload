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

def generate_video_id(file_id):
    hash_object = hashlib.md5(f"{file_id}{datetime.now()}".encode())
    return hash_object.hexdigest()[:12]

def add_user(user_id, username=None, bot_number=1):
    user_data = {
        "user_id": user_id,
        "username": username,
        "bot_number": bot_number,
        "joined_date": datetime.now(),
        "is_banned": False
    }
    users_collection.update_one(
        {"user_id": user_id, "bot_number": bot_number},
        {"$set": user_data},
        upsert=True
    )

def get_user(user_id, bot_number=1):
    return users_collection.find_one({"user_id": user_id, "bot_number": bot_number})

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

def store_video(file_id, file_unique_id, message_id, bot_number=1):
    video_id = generate_video_id(file_id)
    video_data = {
        "video_id": video_id,
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "message_id": message_id,
        "bot_number": bot_number,
        "posted_date": datetime.now(),
        "views": 0
    }
    videos_collection.insert_one(video_data)
    return video_id

def get_video(video_id):
    return videos_collection.find_one({"video_id": video_id})

def increment_video_views(video_id):
    videos_collection.update_one(
        {"video_id": video_id},
        {"$inc": {"views": 1}}
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

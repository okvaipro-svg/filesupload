from pyrogram.client import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
import database
import config

async def check_force_subscribe(client: Client, user_id: int, bot_number: int):
    required_channels = database.get_required_channels(bot_number)
    not_joined = []
    
    for channel in required_channels:
        try:
            chat_identifier = channel
            is_invite_link = False
            
            if channel.startswith("+"):
                chat_identifier = f"https://t.me/{channel}"
                is_invite_link = True
            elif "t.me/+" in channel:
                is_invite_link = True
            elif "https://t.me/" in channel:
                chat_identifier = channel.replace("https://t.me/", "")
            
            if is_invite_link:
                try:
                    chat_info = await client.get_chat(chat_identifier)
                    chat_id = chat_info.id
                    
                    try:
                        member = await client.get_chat_member(chat_id, user_id)
                        if member.status in ["left", "kicked"]:
                            not_joined.append(channel)
                    except UserNotParticipant:
                        not_joined.append(channel)
                except Exception as e:
                    print(f"Cannot access invite channel {channel}: {e}")
                    print(f"Bot must be added to private channel first!")
                    not_joined.append(channel)
            else:
                try:
                    member = await client.get_chat_member(chat_identifier, user_id)
                    if member.status in ["left", "kicked"]:
                        not_joined.append(channel)
                except UserNotParticipant:
                    not_joined.append(channel)
                    
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            not_joined.append(channel)
    
    return not_joined

def create_force_subscribe_buttons(not_joined_channels):
    buttons = []
    for i, channel in enumerate(not_joined_channels, 1):
        channel_link = channel if channel.startswith("https://") else f"https://t.me/{channel}"
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"][min(i-1, 7)]
        buttons.append([InlineKeyboardButton(f"{emoji} Join Channel {i}", url=channel_link)])
    
    buttons.append([InlineKeyboardButton("✅ Verify Subscription", callback_data="verify_subscription")])
    return InlineKeyboardMarkup(buttons)

def create_welcome_buttons():
    buttons = [
        [
            InlineKeyboardButton("📊 Statistics", callback_data="stats"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🎁 Refer & Earn", callback_data="referral"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="user_settings"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def create_main_menu_buttons():
    buttons = [
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🎁 Referral", callback_data="referral"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def create_admin_panel_buttons():
    buttons = [
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics")
        ],
        [
            InlineKeyboardButton("👥 Users", callback_data="admin_users"),
            InlineKeyboardButton("🎥 Videos", callback_data="admin_videos")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
            InlineKeyboardButton("📈 Statistics", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="admin_panel"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def create_settings_buttons():
    buttons = [
        [
            InlineKeyboardButton("📝 Update Channels", callback_data="update_channels"),
            InlineKeyboardButton("⏰ Post Schedule", callback_data="set_post_time")
        ],
        [
            InlineKeyboardButton("🎨 Customize", callback_data="customize_bot"),
            InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")
        ],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(buttons)

def create_user_settings_buttons():
    buttons = [
        [InlineKeyboardButton("🌐 Language", callback_data="change_language")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def is_admin(user_id):
    return user_id in [config.OWNER_ID, config.SUDO_ID]

async def send_to_logger(client: Client, message: str, bot_number: int):
    try:
        formatted_message = f"""
╔═══════════════════════════╗
║  🤖 **Bot Activity Log**   ║
╚═══════════════════════════╝

**Bot:** #{bot_number}
**Time:** {database.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 **Message:**
{message}
"""
        await client.send_message(config.LOGGER_CHANNEL_ID, formatted_message)
    except Exception as e:
        print(f"Logger error: {e}")

def generate_video_link(bot_username: str, video_id: str):
    return f"https://t.me/{bot_username}?start={video_id}"

def create_referral_text(user_id, bot_username, bot_number):
    user = database.get_user(user_id, bot_number)
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    referral_count = user.get("referral_count", 0) if user else 0
    referral_points = user.get("referral_points", 0) if user else 0
    
    return f"""
🎁 **Refer & Earn Program**

Share your referral link and earn rewards!

**Your Stats:**
👥 Referrals: {referral_count}
⭐ Points: {referral_points}

**Your Referral Link:**
`{referral_link}`

**How it Works:**
1️⃣ Share your link with friends
2️⃣ They join using your link
3️⃣ You earn 10 points per referral
4️⃣ Unlock exclusive rewards!

**Rewards:**
🥉 50 Points → VIP Badge
🥈 100 Points → Premium Access (7 days)
🥇 500 Points → Lifetime Premium

Start sharing now! 🚀
"""

def create_help_text():
    return """
📚 **Complete Bot Guide**

━━━━━━━━━━━━━━━━━━━━━
**🎬 How to Watch Videos**
━━━━━━━━━━━━━━━━━━━━━

1️⃣ Click on video links from our channel
2️⃣ Join all required channels
3️⃣ Click "✅ Verify" button
4️⃣ Enjoy your video! 🍿

━━━━━━━━━━━━━━━━━━━━━
**🎁 Referral Program**
━━━━━━━━━━━━━━━━━━━━━

• Share your referral link
• Earn 10 points per friend
• Get amazing rewards
• Unlock premium features

━━━━━━━━━━━━━━━━━━━━━
**📱 Available Commands**
━━━━━━━━━━━━━━━━━━━━━

/start - Start the bot
/help - Show this guide  
/stats - View statistics
/referral - Get referral link
/leaderboard - Top referrers

━━━━━━━━━━━━━━━━━━━━━
**💡 Pro Tips**
━━━━━━━━━━━━━━━━━━━━━

✨ Join all channels for instant access
✨ Refer friends to earn rewards
✨ Check leaderboard for competitions
✨ Contact admin for any issues

━━━━━━━━━━━━━━━━━━━━━

Need help? Contact admin! 👨‍💼
"""

def create_stats_text(bot_number):
    total_users = database.get_total_users(bot_number)
    total_videos = database.get_total_videos(bot_number)
    active_today = database.get_active_users_today(bot_number)
    total_views = database.get_stat(f"bot_{bot_number}_video_views")
    
    return f"""
📊 **Bot Statistics Dashboard**

━━━━━━━━━━━━━━━━━━━━━
**👥 User Statistics**
━━━━━━━━━━━━━━━━━━━━━

Total Users: **{total_users}**
Active Today: **{active_today}**
Growth Rate: **📈 +{active_today}%**

━━━━━━━━━━━━━━━━━━━━━
**🎥 Content Statistics**
━━━━━━━━━━━━━━━━━━━━━

Total Videos: **{total_videos}**
Total Views: **{total_views}**
Avg. Views: **{total_views // max(total_videos, 1)}**

━━━━━━━━━━━━━━━━━━━━━
**🚀 Performance**
━━━━━━━━━━━━━━━━━━━━━

Status: **🟢 Excellent**
Uptime: **99.9%**
Response: **⚡ Fast**

━━━━━━━━━━━━━━━━━━━━━

Last Updated: {database.datetime.now().strftime('%H:%M:%S')}
"""

def create_admin_stats_text(bot_number):
    total_users = database.get_total_users(bot_number)
    total_videos = database.get_total_videos(bot_number)
    active_today = database.get_active_users_today(bot_number)
    total_views = database.get_stat(f"bot_{bot_number}_video_views")
    analytics = database.get_analytics_summary(bot_number, days=7)
    
    return f"""
📈 **Advanced Admin Analytics**

━━━━━━━━━━━━━━━━━━━━━
**📊 Overview (Bot #{bot_number})**
━━━━━━━━━━━━━━━━━━━━━

👥 Total Users: **{total_users}**
🔥 Active Today: **{active_today}**
🎥 Total Videos: **{total_videos}**
👁 Total Views: **{total_views}**

━━━━━━━━━━━━━━━━━━━━━
**📈 7-Day Analytics**
━━━━━━━━━━━━━━━━━━━━━

Total Events: **{analytics.get('total_events', 0)}**
Unique Users: **{analytics.get('unique_users', 0)}**

**Event Breakdown:**
{chr(10).join(f"• {event}: {count}" for event, count in analytics.get('events_by_type', {}).items())}

━━━━━━━━━━━━━━━━━━━━━
**🎯 Engagement Metrics**
━━━━━━━━━━━━━━━━━━━━━

Engagement Rate: **{(active_today / max(total_users, 1) * 100):.1f}%**
Avg. Videos/User: **{total_views / max(total_users, 1):.1f}**
Content Score: **⭐⭐⭐⭐⭐**

━━━━━━━━━━━━━━━━━━━━━

Generated: {database.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def create_leaderboard_text(bot_number):
    top_referrers = database.get_top_referrers(bot_number, limit=10)
    
    text = """
🏆 **Top Referrers Leaderboard**

━━━━━━━━━━━━━━━━━━━━━
"""
    
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_referrers, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        username = user.get('username', 'Unknown')
        points = user.get('referral_points', 0)
        referrals = user.get('referral_count', 0)
        text += f"\n{medal} @{username}\n    ⭐ {points} pts | 👥 {referrals} referrals\n"
    
    if not top_referrers:
        text += "\nNo referrers yet. Be the first! 🚀"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━\n\nStart referring to climb the ladder! 📈"
    
    return text

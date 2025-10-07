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
            channel_username = channel.replace("https://t.me/", "").replace("+", "")
            
            if channel_username.startswith("+"):
                channel_username = channel_username[1:]
            
            member = await client.get_chat_member(channel_username, user_id)
            
            if member.status in ["left", "kicked"]:
                not_joined.append(channel)
        except UserNotParticipant:
            not_joined.append(channel)
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            continue
    
    return not_joined

def create_force_subscribe_buttons(not_joined_channels):
    buttons = []
    for i, channel in enumerate(not_joined_channels, 1):
        channel_link = channel if channel.startswith("https://") else f"https://t.me/{channel}"
        buttons.append([InlineKeyboardButton(f"Join Channel {i}", url=channel_link)])
    
    buttons.append([InlineKeyboardButton("✅ Verify", callback_data="verify_subscription")])
    return InlineKeyboardMarkup(buttons)

def create_main_menu_buttons():
    buttons = [
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    return InlineKeyboardMarkup(buttons)

def create_admin_panel_buttons():
    buttons = [
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def create_settings_buttons():
    buttons = [
        [InlineKeyboardButton("📝 Update Channels", callback_data="update_channels")],
        [InlineKeyboardButton("⏰ Set Post Time", callback_data="set_post_time")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(buttons)

def is_admin(user_id):
    return user_id in [config.OWNER_ID, config.SUDO_ID]

async def send_to_logger(client: Client, message: str, bot_number: int):
    try:
        await client.send_message(
            config.LOGGER_CHANNEL_ID,
            f"**Bot {bot_number}**\n\n{message}"
        )
    except Exception as e:
        print(f"Logger error: {e}")

def generate_video_link(bot_username: str, video_id: str):
    return f"https://t.me/{bot_username}?start={video_id}"

def create_help_text():
    return """
**📚 Help & Commands**

🔹 **How to Use:**
1. Click on video links posted in the channel
2. Join all required channels
3. Click verify to watch the video

🔹 **Available Commands:**
• /start - Start the bot
• /help - Show this help message
• /stats - View bot statistics

🔹 **Need Support?**
Contact the admin for any issues.
"""

def create_stats_text(bot_number):
    total_users = database.get_total_users(bot_number)
    total_videos = database.get_total_videos(bot_number)
    
    return f"""
**📊 Bot Statistics**

👥 Total Users: {total_users}
🎥 Total Videos: {total_videos}

📈 Bot is running smoothly!
"""

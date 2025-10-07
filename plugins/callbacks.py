from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import CallbackQuery
import database
import helpers
import config

@Client.on_callback_query(filters.regex("^verify_subscription$"))
async def verify_subscription(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_number = client.bot_number
    
    not_joined = await helpers.check_force_subscribe(client, user_id, bot_number)
    
    if not_joined:
        await callback_query.answer(
            "❌ Please join all channels first!\n"
            f"Remaining: {len(not_joined)} channel(s)",
            show_alert=True
        )
    else:
        await callback_query.answer("✅ Verified! Sending video...", show_alert=True)
        
        video_id = None
        if hasattr(client, 'temp_video_id') and user_id in client.temp_video_id:
            video_id = client.temp_video_id[user_id]
        
        if video_id:
            video = database.get_video(video_id)
            if video:
                try:
                    await client.copy_message(
                        chat_id=user_id,
                        from_chat_id=config.SAVED_CHANNEL_ID,
                        message_id=video["message_id"]
                    )
                    database.increment_video_views(video_id, user_id)
                    database.update_stats(f"bot_{bot_number}_video_views")
                    
                    success_text = """
✅ **Video Delivered!**

Enjoy your exclusive content! 🎬

━━━━━━━━━━━━━━━━━━━━━
Want more? Share with friends! 🎁
"""
                    await callback_query.message.edit_text(
                        success_text,
                        reply_markup=helpers.create_main_menu_buttons()
                    )
                    
                    del client.temp_video_id[user_id]
                    
                    database.log_analytics_event(bot_number, "video_delivered_after_verify", user_id, {"video_id": video_id})
                    await helpers.send_to_logger(
                        client,
                        f"User {user_id} verified and watched video {video_id}",
                        bot_number
                    )
                except Exception as e:
                    await callback_query.message.reply_text("❌ Error sending video. Please try again later.")
                    print(f"Error: {e}")

@Client.on_callback_query(filters.regex("^stats$"))
async def stats_callback(client: Client, callback_query: CallbackQuery):
    bot_number = client.bot_number
    await callback_query.message.edit_text(
        helpers.create_stats_text(bot_number),
        reply_markup=helpers.create_main_menu_buttons()
    )
    await callback_query.answer("📊 Statistics loaded!")
    database.log_analytics_event(bot_number, "stats_viewed", callback_query.from_user.id)

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        helpers.create_help_text(),
        reply_markup=helpers.create_main_menu_buttons()
    )
    await callback_query.answer("ℹ️ Help information loaded!")
    database.log_analytics_event(client.bot_number, "help_viewed", callback_query.from_user.id)

@Client.on_callback_query(filters.regex("^referral$"))
async def referral_callback(client: Client, callback_query: CallbackQuery):
    bot_number = client.bot_number
    bot_info = await client.get_me()
    
    referral_text = helpers.create_referral_text(
        callback_query.from_user.id,
        bot_info.username,
        bot_number
    )
    
    await callback_query.message.edit_text(referral_text, reply_markup=helpers.create_main_menu_buttons())
    await callback_query.answer("🎁 Referral info loaded!")
    database.log_analytics_event(bot_number, "referral_viewed", callback_query.from_user.id)

@Client.on_callback_query(filters.regex("^leaderboard$"))
async def leaderboard_callback(client: Client, callback_query: CallbackQuery):
    bot_number = client.bot_number
    leaderboard_text = helpers.create_leaderboard_text(bot_number)
    
    await callback_query.message.edit_text(leaderboard_text, reply_markup=helpers.create_main_menu_buttons())
    await callback_query.answer("🏆 Leaderboard loaded!")
    database.log_analytics_event(bot_number, "leaderboard_viewed", callback_query.from_user.id)

@Client.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client: Client, callback_query: CallbackQuery):
    text = """
📱 **Main Menu**

Choose an option from the menu below:
"""
    await callback_query.message.edit_text(text, reply_markup=helpers.create_welcome_buttons())
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^user_settings$"))
async def user_settings_callback(client: Client, callback_query: CallbackQuery):
    text = """
⚙️ **User Settings**

Customize your experience:
"""
    await callback_query.message.edit_text(text, reply_markup=helpers.create_user_settings_buttons())
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer("Message closed!")

@Client.on_callback_query(filters.regex("^admin_panel$"))
async def admin_panel_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    admin_text = """
╔═══════════════════════════╗
║  🔧 **Admin Control Panel**  ║
╚═══════════════════════════╝

**Welcome Admin!** 👨‍💼

**Quick Actions:**
• 📢 Broadcast messages
• 📊 View detailed analytics
• 👥 Manage users
• 🎥 Manage videos
• ⚙️ Configure settings

**Select an option below** 👇
"""
    await callback_query.message.edit_text(admin_text, reply_markup=helpers.create_admin_panel_buttons())
    await callback_query.answer("🔧 Admin panel loaded!")

@Client.on_callback_query(filters.regex("^admin_settings$"))
async def admin_settings_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    text = """
⚙️ **Bot Settings**

Configure your bot settings:

• Update force subscribe channels
• Set posting schedule
• Customize bot appearance
• Manage notifications
"""
    await callback_query.message.edit_text(text, reply_markup=helpers.create_settings_buttons())
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^admin_stats$"))
async def admin_stats_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_number = client.bot_number
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    stats_text = helpers.create_admin_stats_text(bot_number)
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
    await callback_query.answer("📈 Statistics loaded!")

@Client.on_callback_query(filters.regex("^admin_analytics$"))
async def admin_analytics_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_number = client.bot_number
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    analytics_text = helpers.create_admin_stats_text(bot_number)
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(analytics_text, reply_markup=keyboard)
    await callback_query.answer("📊 Analytics loaded!")

@Client.on_callback_query(filters.regex("^admin_users$"))
async def admin_users_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_number = client.bot_number
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    total_users = database.get_total_users(bot_number)
    active_today = database.get_active_users_today(bot_number)
    
    users_text = f"""
👥 **User Management**

━━━━━━━━━━━━━━━━━━━━━
**Statistics:**

Total Users: **{total_users}**
Active Today: **{active_today}**
Inactive: **{total_users - active_today}**

━━━━━━━━━━━━━━━━━━━━━
**Admin Commands:**

`/ban <user_id>` - Ban a user
`/unban <user_id>` - Unban a user
`/users` - Detailed stats

━━━━━━━━━━━━━━━━━━━━━
"""
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(users_text, reply_markup=keyboard)
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^admin_videos$"))
async def admin_videos_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_number = client.bot_number
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    total_videos = database.get_total_videos(bot_number)
    total_views = database.get_stat(f"bot_{bot_number}_video_views")
    trending = database.get_trending_videos(bot_number, limit=5)
    
    videos_text = f"""
🎥 **Video Management**

━━━━━━━━━━━━━━━━━━━━━
**Statistics:**

Total Videos: **{total_videos}**
Total Views: **{total_views}**
Avg. Views: **{total_views // max(total_videos, 1)}**

━━━━━━━━━━━━━━━━━━━━━
**Trending Videos:**

"""
    
    for i, video in enumerate(trending[:5], 1):
        videos_text += f"{i}. 👁 {video.get('views', 0)} views | ID: `{video['video_id']}`\n"
    
    if not trending:
        videos_text += "No videos yet.\n"
    
    videos_text += "\n━━━━━━━━━━━━━━━━━━━━━"
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(videos_text, reply_markup=keyboard)
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^admin_broadcast$"))
async def admin_broadcast_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    text = """
📢 **Broadcast Message**

**How to broadcast:**

1. Reply to any message with `/broadcast`
2. The message will be sent to all users
3. Track delivery status in real-time

**Use wisely!** This sends to all active users.
"""
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()

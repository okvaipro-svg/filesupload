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
        await callback_query.answer("❌ Please join all channels first!", show_alert=True)
    else:
        await callback_query.answer("✅ Verified! Sending video...", show_alert=True)
        
        video_id = getattr(client, 'temp_video_id', {}).get(user_id)
        
        if video_id:
            video = database.get_video(video_id)
            if video:
                try:
                    await client.copy_message(
                        chat_id=user_id,
                        from_chat_id=config.SAVED_CHANNEL_ID,
                        message_id=video["message_id"]
                    )
                    database.increment_video_views(video_id)
                    database.update_stats(f"bot_{bot_number}_video_views")
                    
                    await callback_query.message.delete()
                    
                    if hasattr(client, 'temp_video_id') and user_id in client.temp_video_id:
                        del client.temp_video_id[user_id]
                    
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
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        helpers.create_help_text(),
        reply_markup=helpers.create_main_menu_buttons()
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client: Client, callback_query: CallbackQuery):
    text = """
**📱 Main Menu**

Choose an option below:
"""
    await callback_query.message.edit_text(text, reply_markup=helpers.create_main_menu_buttons())
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^admin_panel$"))
async def admin_panel_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    text = """
**🔧 Admin Panel**

Manage your bot settings and features:
"""
    await callback_query.message.edit_text(text, reply_markup=helpers.create_admin_panel_buttons())
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^admin_settings$"))
async def admin_settings_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if not helpers.is_admin(user_id):
        await callback_query.answer("❌ You don't have permission!", show_alert=True)
        return
    
    text = """
**⚙️ Bot Settings**

Configure your bot settings:
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
    
    total_users = database.get_total_users(bot_number)
    total_videos = database.get_total_videos(bot_number)
    total_views = database.get_stat(f"bot_{bot_number}_video_views")
    
    text = f"""
**📊 Detailed Statistics - Bot {bot_number}**

👥 Total Users: {total_users}
🎥 Total Videos: {total_videos}
👁 Total Video Views: {total_views}

📈 Bot Performance is excellent!
"""
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()

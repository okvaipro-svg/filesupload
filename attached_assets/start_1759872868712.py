from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
import database
import helpers
import config

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot_number = client.bot_number
    
    database.add_user(user_id, username, bot_number)
    
    if len(message.text.split()) > 1:
        video_id = message.text.split()[1]
        
        user = database.get_user(user_id, bot_number)
        if user and user.get("is_banned"):
            await message.reply_text("❌ You are banned from using this bot.")
            return
        
        not_joined = await helpers.check_force_subscribe(client, user_id, bot_number)
        
        if not_joined:
            await message.reply_text(
                "⚠️ **You must join all required channels to access this video!**\n\n"
                "Please join the channels below and click verify:",
                reply_markup=helpers.create_force_subscribe_buttons(not_joined)
            )
            client.temp_video_id = {user_id: video_id}
        else:
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
                    
                    await helpers.send_to_logger(
                        client,
                        f"User {user_id} watched video {video_id}",
                        bot_number
                    )
                except Exception as e:
                    await message.reply_text("❌ Error sending video. Please try again later.")
                    print(f"Error: {e}")
            else:
                await message.reply_text("❌ Video not found!")
    else:
        welcome_text = f"""
**👋 Welcome to the Bot!**

This bot provides exclusive video content. Click on the links shared in the channel to access videos.

**How it works:**
1. Click video link from the channel
2. Join all required channels
3. Verify and watch the video

Use /help for more information.
"""
        await message.reply_text(welcome_text, reply_markup=helpers.create_main_menu_buttons())
        
        await helpers.send_to_logger(
            client,
            f"New user started: {user_id} (@{username})",
            bot_number
        )

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(
        helpers.create_help_text(),
        reply_markup=helpers.create_main_menu_buttons()
    )

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    bot_number = client.bot_number
    await message.reply_text(
        helpers.create_stats_text(bot_number),
        reply_markup=helpers.create_main_menu_buttons()
    )

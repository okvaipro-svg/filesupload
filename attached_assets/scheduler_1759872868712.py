from pyrogram.client import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import database
import helpers
import config
import random

async def post_daily_videos(client: Client):
    bot_number = client.bot_number
    bot_info = await client.get_me()
    bot_username = bot_info.username
    
    try:
        messages = []
        async for message in client.get_chat_history(config.SAVED_CHANNEL_ID, limit=100):
            if message.video:
                messages.append(message)
        
        if len(messages) < 2:
            print(f"Bot {bot_number}: Not enough videos in saved channel")
            return
        
        selected_messages = random.sample(messages, 2)
        
        for msg in selected_messages:
            video_id = database.store_video(
                msg.video.file_id,
                msg.video.file_unique_id,
                msg.id,
                bot_number
            )
            
            video_link = helpers.generate_video_link(bot_username, video_id)
            
            caption = f"🎥 **New Video Available!**\n\n👆 Click the button above to watch\n\n⚡️ Exclusive Content"
            
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Watch Video", url=video_link)]
            ])
            
            await client.send_photo(
                config.MAIN_CHANNEL_ID,
                photo="https://telegra.ph/file/d3f4f5f5f5f5f5f5f5f5f.jpg",
                caption=caption,
                reply_markup=keyboard
            )
        
        await helpers.send_to_logger(
            client,
            f"Posted 2 daily videos to main channel",
            bot_number
        )
        
        database.update_stats(f"bot_{bot_number}_daily_posts")
        
    except Exception as e:
        print(f"Bot {bot_number} posting error: {e}")
        await helpers.send_to_logger(
            client,
            f"Error posting daily videos: {str(e)}",
            bot_number
        )

def setup_scheduler(client: Client):
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        post_daily_videos,
        'cron',
        hour=config.POST_TIME_HOUR,
        minute=config.POST_TIME_MINUTE,
        args=[client]
    )
    
    scheduler.start()
    print(f"Scheduler started for Bot {client.bot_number}")
    
    return scheduler

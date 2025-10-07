import asyncio
from pyrogram.client import Client
from pyrogram import idle
from plugins import scheduler
import config

class BotClient(Client):
    def __init__(self, name, api_id, api_hash, bot_token, bot_number):
        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            plugins=dict(root="plugins")
        )
        self.bot_number = bot_number
        self.temp_video_id = {}

async def start_bot(bot_number, bot_token):
    print(f"Starting Bot {bot_number}...")
    
    bot = BotClient(
        name=f"bot_{bot_number}",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=bot_token,
        bot_number=bot_number
    )
    
    await bot.start()
    
    bot_info = await bot.get_me()
    print(f"Bot {bot_number} started: @{bot_info.username}")
    
    scheduler.setup_scheduler(bot)
    
    return bot

async def main():
    print("🚀 Starting Multi-Bot System...")
    print(f"Total bots to start: {len(config.BOT_TOKENS)}")
    
    bots = []
    
    for i, token in enumerate(config.BOT_TOKENS, start=1):
        if token:
            bot = await start_bot(i, token)
            bots.append(bot)
    
    print(f"\n✅ All {len(bots)} bots are running!")
    print("Press Ctrl+C to stop")
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bots stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

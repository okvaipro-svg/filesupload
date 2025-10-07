import asyncio
from pyrogram.client import Client
from pyrogram import idle
from plugins import scheduler
import config
from datetime import datetime

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

async def send_startup_log(bot, bot_number, bot_username):
    try:
        startup_message = f"""
╔═══════════════════════════════════╗
║  🚀 **BOT STARTED SUCCESSFULLY**  ║
╚═══════════════════════════════════╝

**Bot Information:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Bot Number: **#{bot_number}**
👤 Username: @{bot_username}
⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Status:**
✅ Bot Online
✅ Plugins Loaded
✅ Database Connected
✅ Scheduler Active
✅ Force Subscribe Ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Features Active:**
• 📊 Advanced Analytics
• 🎁 Referral System
• 🏆 Leaderboard
• 📢 Broadcasting
• 🎥 Video Distribution
• ⚙️ Admin Panel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 **System Status: ONLINE**
Bot is ready to serve users! 🎉
"""
        await bot.send_message(config.STARTUP_LOG_GROUP_ID, startup_message)
        print(f"✅ Startup log sent to group for Bot {bot_number}")
    except Exception as e:
        print(f"⚠️ Could not send startup log to group: {e}")

async def start_bot(bot_number, bot_token):
    print(f"🚀 Starting Bot {bot_number}...")
    
    if not config.API_ID or not config.API_HASH:
        print("❌ Error: API_ID and API_HASH are required!")
        print("Please set them in your environment or .env file")
        return None
    
    bot = BotClient(
        name=f"bot_{bot_number}",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=bot_token,
        bot_number=bot_number
    )
    
    await bot.start()
    
    bot_info = await bot.get_me()
    print(f"✅ Bot {bot_number} started: @{bot_info.username}")
    
    scheduler.setup_scheduler(bot)
    
    await send_startup_log(bot, bot_number, bot_info.username)
    
    return bot

async def main():
    print("╔════════════════════════════════════════════╗")
    print("║  🤖 ADVANCED TELEGRAM MULTI-BOT SYSTEM  ║")
    print("╚════════════════════════════════════════════╝")
    print()
    print(f"📊 Total bots to start: {len(config.BOT_TOKENS)}")
    print()
    
    bots = []
    
    for i, token in enumerate(config.BOT_TOKENS, start=1):
        if token:
            bot = await start_bot(i, token)
            if bot:
                bots.append(bot)
    
    if not bots:
        print("❌ No bots started. Please check your configuration.")
        return
    
    print()
    print(f"╔════════════════════════════════════════════╗")
    print(f"║  ✅ ALL {len(bots)} BOTS ARE RUNNING!            ║")
    print(f"╚════════════════════════════════════════════╝")
    print()
    print("📋 Features Active:")
    print("  ✓ Multi-bot system")
    print("  ✓ Advanced admin panel")
    print("  ✓ Beautiful UI & buttons")
    print("  ✓ Force subscribe system")
    print("  ✓ Referral & rewards")
    print("  ✓ Analytics & stats")
    print("  ✓ Automated posting")
    print("  ✓ Broadcast system")
    print()
    print("🔧 Press Ctrl+C to stop all bots")
    print()
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bots stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

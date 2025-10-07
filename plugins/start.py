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
    
    referred_by = None
    if len(message.text.split()) > 1:
        param = message.text.split()[1]
        
        if param.startswith("ref_"):
            referred_by = int(param.split("_")[1])
            database.add_user(user_id, username, bot_number, referred_by)
            
            welcome_text = f"""
🎉 **Welcome via Referral!**

You've joined through a friend's referral link!
Both you and your friend will earn rewards! 🎁

Let's get started! 👇
"""
            await message.reply_text(welcome_text, reply_markup=helpers.create_welcome_buttons())
            
            database.log_analytics_event(bot_number, "referral_signup", user_id, {"referrer": referred_by})
            await helpers.send_to_logger(
                client,
                f"New referral signup: {user_id} (Referred by: {referred_by})",
                bot_number
            )
            return
        
        video_id = param
        database.add_user(user_id, username, bot_number)
        
        user = database.get_user(user_id, bot_number)
        if user and user.get("is_banned"):
            await message.reply_text("❌ You are banned from using this bot.")
            return
        
        not_joined = await helpers.check_force_subscribe(client, user_id, bot_number)
        
        if not_joined:
            force_sub_text = f"""
╔═══════════════════════════╗
║  🔐 **Subscription Required**  ║
╚═══════════════════════════╝

⚠️ **To access this exclusive video, you must join all our channels!**

**Why Join?**
✨ Access premium content
✨ Get daily updates
✨ Exclusive videos & more
✨ Special rewards

**Join the channels below and click verify:** 👇
"""
            msg = await message.reply_text(
                force_sub_text,
                reply_markup=helpers.create_force_subscribe_buttons(not_joined)
            )
            if not hasattr(client, 'temp_video_id'):
                client.temp_video_id = {}
            client.temp_video_id[user_id] = video_id
            
            database.log_analytics_event(bot_number, "force_subscribe_shown", user_id, {"video_id": video_id})
        else:
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
✅ **Video Delivered Successfully!**

Enjoy watching! 🎬🍿

Want more content? Check our channel for latest updates! 📢
"""
                    await message.reply_text(success_text, reply_markup=helpers.create_main_menu_buttons())
                    
                    database.log_analytics_event(bot_number, "video_delivered", user_id, {"video_id": video_id})
                    await helpers.send_to_logger(
                        client,
                        f"User {user_id} watched video {video_id}",
                        bot_number
                    )
                except Exception as e:
                    await message.reply_text("❌ Error sending video. Please try again later.")
                    print(f"Error: {e}")
            else:
                await message.reply_text("❌ Video not found or expired!")
    else:
        database.add_user(user_id, username, bot_number)
        
        welcome_text = f"""
╔═══════════════════════════╗
║  👋 **Welcome to the Bot!**  ║
╚═══════════════════════════╝

Hello **{message.from_user.first_name}**! 🎉

🎬 **Your Premium Video Hub**

Get access to exclusive video content delivered directly to your DM!

━━━━━━━━━━━━━━━━━━━━━
**✨ Features:**

🎥 High-Quality Videos
📱 Instant Delivery
🎁 Referral Rewards
🏆 Leaderboard System
📊 Track Your Stats

━━━━━━━━━━━━━━━━━━━━━
**🚀 How to Get Started:**

1️⃣ Click video links from our channel
2️⃣ Join all required channels
3️⃣ Verify and watch instantly
4️⃣ Share with friends & earn rewards

━━━━━━━━━━━━━━━━━━━━━

**Explore the menu below** 👇
"""
        
        await message.reply_photo(
            photo=config.WELCOME_IMAGE,
            caption=welcome_text,
            reply_markup=helpers.create_welcome_buttons()
        )
        
        database.log_analytics_event(bot_number, "new_user", user_id)
        await helpers.send_to_logger(
            client,
            f"✨ New user started: {user_id} (@{username})\nName: {message.from_user.first_name}",
            bot_number
        )

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(
        helpers.create_help_text(),
        reply_markup=helpers.create_main_menu_buttons()
    )
    database.log_analytics_event(client.bot_number, "help_viewed", message.from_user.id)

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    bot_number = client.bot_number
    await message.reply_text(
        helpers.create_stats_text(bot_number),
        reply_markup=helpers.create_main_menu_buttons()
    )
    database.log_analytics_event(bot_number, "stats_viewed", message.from_user.id)

@Client.on_message(filters.command(["referral", "refer"]) & filters.private)
async def referral_command(client: Client, message: Message):
    bot_number = client.bot_number
    bot_info = await client.get_me()
    
    referral_text = helpers.create_referral_text(
        message.from_user.id,
        bot_info.username,
        bot_number
    )
    
    await message.reply_text(referral_text, reply_markup=helpers.create_main_menu_buttons())
    database.log_analytics_event(bot_number, "referral_viewed", message.from_user.id)

@Client.on_message(filters.command("leaderboard") & filters.private)
async def leaderboard_command(client: Client, message: Message):
    bot_number = client.bot_number
    leaderboard_text = helpers.create_leaderboard_text(bot_number)
    
    await message.reply_text(leaderboard_text, reply_markup=helpers.create_main_menu_buttons())
    database.log_analytics_event(bot_number, "leaderboard_viewed", message.from_user.id)

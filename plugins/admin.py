from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
import helpers
import database
import config

@Client.on_message(filters.command("admin") & filters.private)
async def admin_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission to access admin panel!")
        return
    
    admin_text = """
╔═══════════════════════════╗
║  🔧 **Admin Control Panel**  ║
╚═══════════════════════════╝

**Welcome Admin!** 👨‍💼

Manage your bot with powerful admin tools.

**Quick Actions:**
• 📢 Broadcast messages
• 📊 View detailed analytics  
• 👥 Manage users
• 🎥 Manage videos
• ⚙️ Configure settings

**Select an option below** 👇
"""
    
    await message.reply_photo(
        photo=config.ADMIN_PANEL_IMAGE,
        caption=admin_text,
        reply_markup=helpers.create_admin_panel_buttons()
    )
    
    database.log_analytics_event(client.bot_number, "admin_panel_accessed", user_id)

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    if message.reply_to_message:
        bot_number = client.bot_number
        users = database.get_all_user_ids(bot_number)
        
        success = 0
        failed = 0
        blocked = 0
        
        status_msg = await message.reply_text(
            f"📢 **Starting Broadcast...**\n\n"
            f"Total Recipients: **{len(users)}**\n"
            f"Status: ⏳ Processing..."
        )
        
        for i, uid in enumerate(users, 1):
            try:
                await message.reply_to_message.copy(uid)
                success += 1
                
                if i % 50 == 0:
                    await status_msg.edit_text(
                        f"📢 **Broadcasting...**\n\n"
                        f"Progress: **{i}/{len(users)}**\n"
                        f"✅ Success: **{success}**\n"
                        f"❌ Failed: **{failed}**"
                    )
            except Exception as e:
                failed += 1
                if "blocked" in str(e).lower():
                    blocked += 1
                print(f"Failed to send to {uid}: {e}")
        
        await status_msg.edit_text(
            f"✅ **Broadcast Completed!**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**Results:**\n"
            f"✓ Success: **{success}**\n"
            f"✗ Failed: **{failed}**\n"
            f"🚫 Blocked: **{blocked}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Success Rate: **{(success/len(users)*100):.1f}%**"
        )
        
        await helpers.send_to_logger(
            client,
            f"📢 Broadcast completed by Admin {user_id}\n\n"
            f"Total: {len(users)}\n"
            f"Success: {success}\n"
            f"Failed: {failed}\n"
            f"Blocked: {blocked}",
            bot_number
        )
        
        database.log_analytics_event(bot_number, "broadcast_sent", user_id, {
            "total": len(users), "success": success, "failed": failed
        })
    else:
        await message.reply_text(
            "⚠️ **How to Broadcast:**\n\n"
            "1. Create/forward the message you want to send\n"
            "2. Reply to it with `/broadcast`\n"
            "3. Bot will send it to all users\n\n"
            "**Reply to a message to broadcast it!**"
        )

@Client.on_message(filters.command("users") & filters.private)
async def users_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    bot_number = client.bot_number
    total_users = database.get_total_users(bot_number)
    active_today = database.get_active_users_today(bot_number)
    
    users_text = f"""
👥 **User Statistics**

━━━━━━━━━━━━━━━━━━━━━
**Overview:**

Total Users: **{total_users}**
Active Today: **{active_today}**
Inactive: **{total_users - active_today}**

━━━━━━━━━━━━━━━━━━━━━
**Engagement:**

Active Rate: **{(active_today/max(total_users,1)*100):.1f}%**
Status: **{'🟢 Excellent' if active_today/max(total_users,1) > 0.3 else '🟡 Good' if active_today/max(total_users,1) > 0.1 else '🔴 Needs Boost'}**

━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.reply_text(users_text)

@Client.on_message(filters.command("ban") & filters.private)
async def ban_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "⚠️ **Usage:** `/ban <user_id>`\n\n"
            "Example: `/ban 123456789`"
        )
        return
    
    try:
        target_user_id = int(message.command[1])
        bot_number = client.bot_number
        database.ban_user(target_user_id, bot_number)
        
        await message.reply_text(
            f"✅ **User Banned Successfully!**\n\n"
            f"User ID: `{target_user_id}`\n"
            f"Status: 🚫 Banned"
        )
        
        await helpers.send_to_logger(
            client,
            f"🚫 User {target_user_id} banned by Admin {user_id}",
            bot_number
        )
        
        database.log_analytics_event(bot_number, "user_banned", user_id, {"target": target_user_id})
    except ValueError:
        await message.reply_text("❌ Invalid user ID! Please provide a valid number.")

@Client.on_message(filters.command("unban") & filters.private)
async def unban_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "⚠️ **Usage:** `/unban <user_id>`\n\n"
            "Example: `/unban 123456789`"
        )
        return
    
    try:
        target_user_id = int(message.command[1])
        bot_number = client.bot_number
        database.unban_user(target_user_id, bot_number)
        
        await message.reply_text(
            f"✅ **User Unbanned Successfully!**\n\n"
            f"User ID: `{target_user_id}`\n"
            f"Status: ✅ Active"
        )
        
        await helpers.send_to_logger(
            client,
            f"✅ User {target_user_id} unbanned by Admin {user_id}",
            bot_number
        )
        
        database.log_analytics_event(bot_number, "user_unbanned", user_id, {"target": target_user_id})
    except ValueError:
        await message.reply_text("❌ Invalid user ID! Please provide a valid number.")

@Client.on_message(filters.command("analytics") & filters.private)
async def analytics_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    bot_number = client.bot_number
    analytics_text = helpers.create_admin_stats_text(bot_number)
    
    await message.reply_text(analytics_text, reply_markup=helpers.create_admin_panel_buttons())

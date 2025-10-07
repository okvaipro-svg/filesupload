from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
import helpers
import database

@Client.on_message(filters.command("admin") & filters.private)
async def admin_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission to access admin panel!")
        return
    
    text = """
**🔧 Admin Panel**

Manage your bot settings and features:
"""
    await message.reply_text(text, reply_markup=helpers.create_admin_panel_buttons())

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
        
        status_msg = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
        
        for user_id in users:
            try:
                await message.reply_to_message.copy(user_id)
                success += 1
            except Exception as e:
                failed += 1
                print(f"Failed to send to {user_id}: {e}")
        
        await status_msg.edit_text(
            f"✅ Broadcast completed!\n\n"
            f"✓ Success: {success}\n"
            f"✗ Failed: {failed}"
        )
        
        await helpers.send_to_logger(
            client,
            f"Broadcast completed by {message.from_user.id}\nSuccess: {success}, Failed: {failed}",
            bot_number
        )
    else:
        await message.reply_text("⚠️ Reply to a message to broadcast it!")

@Client.on_message(filters.command("users") & filters.private)
async def users_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    bot_number = client.bot_number
    total_users = database.get_total_users(bot_number)
    
    await message.reply_text(f"👥 **Total Users:** {total_users}")

@Client.on_message(filters.command("ban") & filters.private)
async def ban_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    if len(message.command) < 2:
        await message.reply_text("⚠️ Usage: /ban <user_id>")
        return
    
    try:
        target_user_id = int(message.command[1])
        bot_number = client.bot_number
        database.ban_user(target_user_id, bot_number)
        await message.reply_text(f"✅ User {target_user_id} has been banned!")
        
        await helpers.send_to_logger(
            client,
            f"User {target_user_id} banned by {user_id}",
            bot_number
        )
    except ValueError:
        await message.reply_text("❌ Invalid user ID!")

@Client.on_message(filters.command("unban") & filters.private)
async def unban_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not helpers.is_admin(user_id):
        await message.reply_text("❌ You don't have permission!")
        return
    
    if len(message.command) < 2:
        await message.reply_text("⚠️ Usage: /unban <user_id>")
        return
    
    try:
        target_user_id = int(message.command[1])
        bot_number = client.bot_number
        database.unban_user(target_user_id, bot_number)
        await message.reply_text(f"✅ User {target_user_id} has been unbanned!")
        
        await helpers.send_to_logger(
            client,
            f"User {target_user_id} unbanned by {user_id}",
            bot_number
        )
    except ValueError:
        await message.reply_text("❌ Invalid user ID!")

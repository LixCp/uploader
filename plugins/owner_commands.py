# owner_commands.py

from pyrogram import Client, filters
import config
from assets.db import get_total_users

@Client.on_message(filters.command("total") & filters.user(config.owner_id))
async def total_users(client, message):
    total = get_total_users()
    await message.reply_text(f"Total number of users: {total}")

@Client.on_message(filters.command("total"))
async def unauthorized_access(client, message):
    if message.from_user.id != config.owner_id:
        await message.reply_text("You are not authorized to use this command.")

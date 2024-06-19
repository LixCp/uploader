# verify_channel.py

from pyrogram import Client, errors
import config
import asyncio

async def verify_channel(client: Client):
    try:
        chat = await client.get_chat(config.required_channel_id)
        print(f"Bot is in the chat: {chat.title}")

        async for admin in client.get_chat_members(chat_id=config.required_channel_id, filter="administrators"):
            print(f"Admin: {admin.user.first_name}")
            if admin.user.is_self:
                print("Bot is an admin in the channel.")
                return True

        print("Bot is NOT an admin in the channel.")
        return False
    except errors.ChatAdminRequired:
        print("Bot needs to be an admin in the channel.")
    except errors.ChatInvalid:
        print("Invalid channel ID.")
    except errors.ChatIdInvalid:
        print("Invalid chat ID provided.")
    except errors.PeerIdInvalid:
        print("Invalid peer ID.")
    except Exception as e:
        print(f"Unexpected error verifying channel: {e}")
    return False

# Run the verification
async def main():
    client = Client("url_uploader_bot", api_id=config.api_id, api_hash=config.api_hash, bot_token=config.bot_token)
    await client.start()
    await verify_channel(client)
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())

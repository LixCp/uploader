# subscription_check.py

from pyrogram import Client, errors
import config

async def is_subscribed(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(config.required_channel_id, user_id)
        print(member.status)
        return member.status not in ("kicked", "left")
    except errors.UserNotParticipant:
        print("User is not a participant in the channel.")
        return False
    except errors.ChatAdminRequired:
        print("Bot needs to be an admin in the channel to check memberships.")
        return False
    except errors.ChatInvalid:
        print("Invalid channel ID.")
        return False
    except errors.ChatIdInvalid:
        print("Invalid chat ID provided.")
        return False
    except errors.PeerIdInvalid:
        print("Invalid peer ID.")
        return False
    except Exception as e:
        print(f"Unexpected error checking subscription: {e}")
        return False
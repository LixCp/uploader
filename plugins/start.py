# plugins/start.py

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .download import download_file
from .upload import upload_file
from .upload_large import upload_large_file
from .utils import get_file_type, create_video_thumbnail
import config
import logging
import aiohttp
from assets import messages # Import the messages
from assets.db import  get_or_create_user, set_download_status, get_download_status, remove_download_status, can_upload_large_file, update_large_file_upload_time
from .force import is_subscribed  # Import the subscription check


# Configure logging
logging.basicConfig(level=logging.INFO)

# Dictionary to hold cancel tokens for each user
cancel_tokens = {}
# Semaphore to limit the number of concurrent downloads/uploads
max_concurrent_tasks = 10
semaphore = asyncio.Semaphore(max_concurrent_tasks)

# Command to handle the /start message
@Client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    logging.info(f"User {user_id} issued /start command.")

    # Check if the user is subscribed
    if not await is_subscribed(client, user_id):
        await message.reply_text(messages.JOINED_MESSAGE)
        return
    
    get_or_create_user(user_id)  # Add the user to the database
    await message.reply_text(messages.START_MESSAGE)
    logging.info(f"User {user_id} added to the database.")

# Command to handle URL messages
@Client.on_message(filters.text & ~filters.command("start"))
async def handle_url(client, message):
    user_id = message.from_user.id
    logging.info(f"User {user_id} sent a URL: {message.text}")

    # Check if the user is subscribed
    if not await is_subscribed(client, user_id):
        await message.reply_text(messages.JOINED_MESSAGE)
        return

    user_status = get_download_status(user_id)
    if user_status:
        await message.reply_text(messages.DOWNLOAD_IN_PROGRESS)
        logging.info(f"User {user_id} already has a download in progress.")
        return

    url = message.text
    filename = os.path.basename(url)  # Extract the filename from the URL
    filepath = os.path.join("downloads", filename)  # Define the full file path

    cancel_event = asyncio.Event()
    cancel_tokens[user_id] = cancel_event
    set_download_status(user_id, True)  # Mark download as in progress
    logging.info(f"Download status set for user {user_id}.")

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="cancel")]])
    progress_message = await message.reply_text(messages.DOWNLOADING.format(filename=filename), reply_markup=keyboard)

    async with semaphore:
        try:
            download_successful = await download_file(client, url, filepath, progress_message, cancel_event)
            if not download_successful or cancel_event.is_set():
                return

            file_type = get_file_type(filepath)
            
            await progress_message.edit_text(messages.UPLOAD_READY.format(filename=filename), reply_markup=keyboard)
            if cancel_event.is_set():
                return

            if os.path.getsize(filepath) > 2 * 1024 * 1024 * 1024:  # Check if file is larger than 2GB
                if not can_upload_large_file(user_id):
                    await progress_message.edit_text(messages.LARGEUPLOAD_LIMIT)
                    return
                
                thumbnail_path = create_video_thumbnail(filepath) if file_type.startswith("video/") else None
                account_client = Client("account_session", api_id=config.api_id, api_hash=config.api_hash, session_string=config.account_session_string)
                await account_client.start()
                message_id = await upload_large_file(account_client, filepath, file_type, progress_message, cancel_event, client, user_id, thumbnail_path)
                await account_client.stop()

                # Debug statement to check the message_id
                logging.debug(f"DEBUG: Message ID to be copied: {message_id}")

                # Copy the file from the upload chat to the user
                await client.copy_message(chat_id=user_id, from_chat_id=config.upload_chat_id, message_id=message_id)
                update_large_file_upload_time(user_id)  # Update the timestamp for large file upload
                logging.info(f"Large file uploaded for user {user_id}.")
            else:
                thumbnail_path = create_video_thumbnail(filepath) if file_type.startswith("video/") else None
                await upload_file(client, message.chat.id, filepath, file_type, progress_message, cancel_event, thumbnail_path)

            if cancel_event.is_set():
                return

            os.remove(filepath)  # Clean up the downloaded file
            await progress_message.edit_text(messages.DOWNLOAD_SUCCESS.format(filename=filename))
            logging.info(f"File {filename} successfully uploaded for user {user_id}.")
        except aiohttp.ClientError as e:
            await progress_message.edit_text(messages.HTTP_ERROR.format(error=str(e)))
            logging.error(f"HTTP error occurred: {e}")
        except Exception as e:
            await progress_message.edit_text(messages.GENERAL_ERROR.format(error=str(e)))
            logging.error(f"General error occurred: {e}")
        finally:
            remove_download_status(user_id)  # Remove the download status after completion
            logging.info(f"Download status removed for user {user_id}.")

# Handle the cancel callback query
@Client.on_callback_query(filters.regex("cancel"))
async def cancel_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in cancel_tokens:
        cancel_tokens[user_id].set()
        await callback_query.answer(messages.CANCEL_OPERATION)
        del cancel_tokens[user_id]
        remove_download_status(user_id)  # Remove the download status on cancelation
        logging.info(f"Download cancelled for user {user_id}.")
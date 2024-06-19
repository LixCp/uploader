# plugins/upload_large.py

import os
import time
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import Message
from .utils import generate_progress_bar, format_time, get_video_dimensions, create_video_thumbnail, get_file_type
import config

async def upload_large_file(account_client: Client, filepath: str, file_type: str, progress_message: Message, cancel_event, bot: Client, user_chat_id: int, thumbnail_path=None):
    total_size = os.path.getsize(filepath)
    uploaded_size = 0
    start_time = time.time()
    last_update_time = datetime.now()

    def progress(current, total):
        nonlocal uploaded_size
        nonlocal start_time
        nonlocal last_update_time
        uploaded_size = current
        elapsed_time = time.time() - start_time
        progress = uploaded_size / total_size
        speed = uploaded_size / elapsed_time if elapsed_time > 0 else 0
        time_left = (total_size - uploaded_size) / speed if speed > 0 else 0
        progress_bar = generate_progress_bar(progress)
        
        # Update the message every 10 seconds
        if datetime.now() - last_update_time > timedelta(seconds=10):
            progress_message.edit_text(f"Uploading:\n{progress_bar} {progress*100:.2f}%\nTime left: {format_time(time_left)}")
            last_update_time = datetime.now()

    # Ensure interaction with the upload chat
    await account_client.send_message(chat_id=config.upload_chat_id, text="Preparing to upload a large file...")

    if file_type.startswith("image/"):
        message = await account_client.send_photo(chat_id=config.upload_chat_id, photo=filepath, progress=progress)
    elif file_type.startswith("video/"):
        width, height = get_video_dimensions(filepath)
        message = await account_client.send_video(chat_id=config.upload_chat_id, video=filepath, thumb=thumbnail_path, width=width, height=height, progress=progress)
    elif file_type.startswith("audio/") or file_type == "audio/mpeg":
        message = await account_client.send_audio(chat_id=config.upload_chat_id, audio=filepath, progress=progress)
    else:
        message = await account_client.send_document(chat_id=config.upload_chat_id, document=filepath, progress=progress)

    return message.id  # Use the `id` attribute of the returned message

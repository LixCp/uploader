# plugins/upload.py

import os
import time
from datetime import datetime, timedelta
from pyrogram import Client
from .utils import generate_progress_bar, format_time, get_video_dimensions, create_video_thumbnail

async def upload_file(client: Client, chat_id: int, filepath: str, file_type: str, message, cancel_event, thumbnail_path=None):
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
        if datetime.now() - last_update_time > timedelta(seconds=3):
            message.edit_text(f"Uploading:\n{progress_bar} {progress*100:.2f}%\nTime left: {format_time(time_left)}")
            last_update_time = datetime.now()

    if file_type.startswith("image/"):
        await client.send_photo(chat_id=chat_id, photo=filepath, progress=progress)
    elif file_type.startswith("video/"):
        width, height = get_video_dimensions(filepath)
        await client.send_video(chat_id=chat_id, video=filepath, thumb=thumbnail_path, width=width, height=height, progress=progress)
    elif file_type.startswith("audio/") or file_type == "audio/mpeg":
        await client.send_audio(chat_id=chat_id, audio=filepath, progress=progress)
    else:
        await client.send_document(chat_id=chat_id, document=filepath, progress=progress)
    print()

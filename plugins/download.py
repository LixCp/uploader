# plugins/download.py

import aiohttp
import aiofiles
import os
import time
from datetime import datetime, timedelta
from pyrogram import Client
from .utils import generate_progress_bar, format_time

async def download_file(client: Client, url: str, filepath: str, message, cancel_event):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                total_size = int(response.headers.get('content-length', 0))
                chunk_size = 8192
                downloaded_size = 0
                start_time = time.time()
                last_update_time = datetime.now()

                async with aiofiles.open(filepath, "wb") as file:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if cancel_event.is_set():
                            await message.edit_text("Download canceled.")
                            return False
                        await file.write(chunk)
                        downloaded_size += len(chunk)
                        elapsed_time = time.time() - start_time
                        progress = downloaded_size / total_size
                        speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                        time_left = (total_size - downloaded_size) / speed if speed > 0 else 0
                        progress_bar = generate_progress_bar(progress)
                        
                        # Update the message every 10 seconds
                        if datetime.now() - last_update_time > timedelta(seconds=3):
                            await message.edit_text(f"Downloading:\n{progress_bar} {progress*100:.2f}%\nTime left: {format_time(time_left)}")
                            last_update_time = datetime.now()
                # Final update
                await message.edit_text(f"Downloading:\n{progress_bar} {progress*100:.2f}%\nTime left: 0s")
                print()
                return True
            else:
                raise Exception(f"Failed to download file, status code: {response.status}")

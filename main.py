# main.py

from pyrogram import Client
import config
import logging,os

# Configure logging
logging.basicConfig(level=logging.INFO)

if not os.path.exists("downloads"):
    os.makedirs("downloads")
proxy = {
    "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
    "hostname": "127.0.0.1",
    "port": 2080,

}
plugins = dict(root="plugins")
# Initialize the bot with your API ID, API hash, and bot token
app = Client("url_uploader_bot", api_id=config.api_id, api_hash=config.api_hash, bot_token=config.bot_token,plugins=plugins)

# Load plugins

# Run the bot
app.run()

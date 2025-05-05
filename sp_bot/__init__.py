import logging
import os
import sys
import telegram.ext as tg
from sp_bot.config import Config

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# Create Config instance for database operations
config_instance = Config()

# import ENV variables
TOKEN = Config.API_KEY

# spotify secrets
CLIENT_ID = Config.SPOTIFY_CLIENT_ID
CLIENT_SECRET = Config.SPOTIFY_CLIENT_SECRET
REDIRECT_URI = Config.REDIRECT_URI

# JSON Blob ID for Cloudflare Worker
JSON_BLOB_ID = Config.JSON_BLOB_ID

# MongoDB legacy variables - kept for backward compatibility
MONGO_USR = Config.MONGO_USR
MONGO_PASS = Config.MONGO_PASS
COL = Config.MONGO_COLL

# PostgreSQL config - Made available for database operations
config = config_instance

TEMP_CHANNEL = Config.TEMP_CHANNEL

updater = tg.Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

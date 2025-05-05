import re
import importlib
import logging

from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, Filters, MessageHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram.ext.dispatcher import run_async, DispatcherHandlerStop, Dispatcher
from telegram.utils.helpers import escape_markdown

from sp_bot.modules import ALL_MODULES
from sp_bot import dispatcher, updater, LOGGER, TOKEN
from sp_bot.modules.misc.request_spotify import SPOTIFY
from sp_bot.modules.misc.auth_worker import CLOUDFLARE_AUTH
from sp_bot.modules.db import DATABASE

START_TEXT = '''
Hi {},

Follow these steps to start using the bot -
1. Use /register to connect your spotify account with this bot.
2. Open the provided link, give access to the bot & you will be redirected to bot's telegram link.
3. When you open that link you will be redirected back to telegram, click start.
4. After you see a 'successful' message use /name to set a display name (this will be displayed on the song status).

thats it! you can then share your song status using -
/now or using the inline query @bot.

You can also use /linkfm to connect your lastfm account.
Then set a display name using /namefm.
and use /last to share song status.

use /style to change background style.
use /help to get the list of commands.
'''

HELP_TEXT = '''
Heres the list of commands -

/now - share currently playing song on spotify.
/name - change your display name on song status.
/unregister - to unlink your spotify account from the bot.
/register - to connect your spotify account with the bot.
/style - change background style to blur or black.
@bot - share song using inline query

/last - share lastfm song status.
/linkfm - link LastFm account with the bot.
/namefm - set display name for LastFm status.
/unlinkfm - unlink LastFm account from bot.
/status - recently played song via LastFm.

'''

IMPORTED = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("sp_bot.modules." + module_name)

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception(
            "Can't have two modules with the same name! Please change one")


# /start command
def start(update: Update, context: CallbackContext):
    if update.effective_chat.type == update.effective_chat.PRIVATE:
        first_name = update.effective_user.first_name
        text = update.effective_message.text
        if len(text) <= 10:
            update.effective_message.reply_text(
                START_TEXT.format(first_name), parse_mode=ParseMode.MARKDOWN)
        elif text.endswith('register'):
            update.message.reply_text(
                "To register your account use /register command.")
        elif text.endswith('username'):
            update.message.reply_text(
                "To change your username use /name command.")
        elif text.endswith('token'):
            update.message.reply_text(
                "use /unregister to unlink your account & register again using /register command.")
        elif text.endswith('notsure'):
            update.message.reply_text("I'm not sure what you're listening to.")
        elif text.endswith('ads'):
            update.message.reply_text(
                "You're listening to ads!")
        elif text.endswith('notlistening'):
            update.message.reply_text(
                "You're not listening to anything on Spotify at the moment.")
        elif text.endswith('lastfm'):
            update.message.reply_text(
                "To link your lastfm account use /lastfm command.")
        else:
            # Extract the key from the start parameter (e.g., /start abc123)
            key = text[7:]
            if len(key) == 4:  # Key from Cloudflare Worker is 4 characters
                LOGGER.info(f"Received key: {key} from user: {update.effective_user.id}")
                
                try:
                    # Fetch the auth code from JSON Blob using the key
                    auth_code = CLOUDFLARE_AUTH.fetch_auth_code(key)
                    
                    if not auth_code:
                        update.message.reply_text(
                            "Invalid or expired authentication key. Please try again using /register.")
                        return ConversationHandler.END
                    
                    # Check if user is already registered
                    tg_id = str(update.effective_user.id)
                    is_user = DATABASE.fetchData(tg_id)
                    
                    if is_user:
                        update.message.reply_text(
                            "You are already registered. If the bot is not working, use /unregister and then /register again.")
                        return ConversationHandler.END
                    
                    # Get refresh token from Spotify
                    refresh_token = SPOTIFY.getAccessToken(auth_code)
                    
                    if refresh_token == 'error':
                        update.message.reply_text(
                            "Unable to authenticate with Spotify. Please try again using /register. If you continue to have issues, contact support.")
                        return ConversationHandler.END
                    
                    # Add user to database
                    user = DATABASE.addUser(tg_id, refresh_token)
                    
                    if user:
                        update.message.reply_text(
                            "Account successfully linked! 🎉 Now use /name to set a display name, then use /now to share your currently playing song.")
                    else:
                        update.message.reply_text(
                            "There was a problem saving your account. Please try again or contact support.")
                    
                except Exception as ex:
                    LOGGER.exception(f"Error during authentication: {ex}")
                    update.message.reply_text(
                        "An error occurred during authentication. Please try again using /register.")
                    return ConversationHandler.END
            else:
                update.message.reply_text(
                    "Invalid start parameter. Please use /register to begin the registration process.")

        update.effective_message.delete()
        return ConversationHandler.END
    else:
        update.effective_message.reply_text("Hmm?")
        return ConversationHandler.END


# /help command
def get_help(update: Update, context: CallbackContext):
    # ONLY send help in PM
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        update.effective_message.reply_text("Contact me in PM to get the list of possible commands.",
                                            reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="Help",
                                                                       url="t.me/{}?start=help".format(
                                                                           context.bot.username))]]))
        return

    else:
        update.effective_message.reply_text(
            HELP_TEXT, parse_mode=ParseMode.MARKDOWN)


# main
def main():
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", get_help)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()

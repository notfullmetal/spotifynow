from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler

from sp_bot import dispatcher
from sp_bot.modules.db import DATABASE
from sp_bot.modules.misc.request_spotify import SPOTIFY

PM_MSG = 'Contact me in pm to /register or /unregister your account.'
REG_MSG = 'Open the link below, to connect your Spotify account. After authentication, you will be redirected back to Telegram.'
UNREG_MSG = 'Your account has been unlinked successfully.'
BOT_URL = 't.me/{}'


def register(update: Update, context: CallbackContext) -> None:
    'add new user'
    if update.effective_chat.type == update.effective_chat.PRIVATE:
        tg_id = str(update.effective_user.id)
        # Check if user is already registered
        user = DATABASE.fetchData(tg_id)
        if user:
            update.effective_message.reply_text(
                "You are already registered. If you're having issues, use /unregister first and then register again."
            )
            return ConversationHandler.END
        
        # Generate Spotify auth URL
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Open this link to register", url=SPOTIFY.getAuthUrl())]])
        update.effective_message.reply_text(
            REG_MSG, reply_markup=button)
        
        # Provide instructions for after authentication
        update.effective_message.reply_text(
            "After connecting your Spotify account, you'll be redirected to Telegram with a special key. "
            "Just tap 'Start' and the bot will automatically link your account."
        )
        return ConversationHandler.END
    else:
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Register here", url=BOT_URL.format(context.bot.username))]])
        update.effective_message.reply_text(
            PM_MSG, reply_markup=button)
        return ConversationHandler.END


def unregister(update: Update, context: CallbackContext) -> None:
    'remove user from database'
    if update.effective_chat.type == update.effective_chat.PRIVATE:
        tg_id = str(update.effective_user.id)
        # Check if user exists in database
        user = DATABASE.fetchData(tg_id)
        if user:
            DATABASE.deleteData(tg_id)
            update.effective_message.reply_text(UNREG_MSG)
        else:
            update.effective_message.reply_text(
                "You are not registered. Use /register to connect your Spotify account."
            )
        return ConversationHandler.END
    else:
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Unregister here", url=BOT_URL.format(context.bot.username))]])
        update.effective_message.reply_text(
            PM_MSG, reply_markup=button)
        return ConversationHandler.END


# Add handlers
dispatcher.add_handler(CommandHandler("register", register))
dispatcher.add_handler(CommandHandler("unregister", unregister))

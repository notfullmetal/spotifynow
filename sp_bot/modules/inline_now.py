import requests
import json
from uuid import uuid4

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultCachedPhoto
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, InlineQueryHandler

from sp_bot import dispatcher, TEMP_CHANNEL
from sp_bot.modules.misc.cook_image import drawImage
from sp_bot.modules.db import DATABASE
from sp_bot.modules.misc.request_spotify import SPOTIFY


def inlineNowPlaying(update: Update, context: CallbackContext):
    'inline implementation of nowPlaying() function along with exception handeling for new users'
    try:
        tg_id = str(update.inline_query.from_user.id)
        is_user = DATABASE.fetchData(tg_id)
        if is_user == None:
            update.inline_query.answer(
                [], switch_pm_text="You need to register first.", switch_pm_parameter='register', cache_time=0)
            return ConversationHandler.END
        elif is_user["username"] == 'User':
            update.inline_query.answer(
                [], switch_pm_text="You need to set a username.", switch_pm_parameter='username', cache_time=0)
            return ConversationHandler.END
        elif is_user['token'] == '00000':
            update.inline_query.answer(
                [], switch_pm_text="Registration error, please click here to fix.", switch_pm_parameter='token', cache_time=0)
            return ConversationHandler.END
        else:
            token = is_user["token"]
            r = SPOTIFY.getCurrentyPlayingSong(token)
    except Exception as ex:
        print(f"Error in initial setup of inlineNowPlaying: {ex}")
        update.inline_query.answer([], switch_pm_text="An error occurred. Please try again.", 
                                 switch_pm_parameter='error', cache_time=0)
        return

    try:
        # Get the active profile pic
        try:
            chat = context.bot.getChat(tg_id)
            if chat.photo:
                pfp_url = chat.photo.big_file_id
                pfp = requests.get(context.bot.getFile(pfp_url).file_path)
            else:
                pfp = None
        except Exception as e:
            print(f"Error getting profile picture: {e}")
            pfp = None

        # Check if we got a valid response from Spotify
        if r is None or r.status_code != 200 or not r.text:
            # Handle non-200 status codes or empty responses
            if r is None:
                print("Spotify API request returned None")
                update.inline_query.answer([], switch_pm_text="Failed to connect to Spotify.", 
                                          switch_pm_parameter='connection', cache_time=0)
            elif r.status_code == 204:
                update.inline_query.answer([], switch_pm_text="You're not playing anything on Spotify.",
                                          switch_pm_parameter='nothing', cache_time=0)
            else:
                print(f"Spotify API returned status code: {r.status_code}")
                update.inline_query.answer([], switch_pm_text="Issue connecting to Spotify. Try again.",
                                          switch_pm_parameter='statuserror', cache_time=0)
            return

        try:
            res = r.json()
        except json.JSONDecodeError as json_err:
            print(f"JSON Parse Error: {json_err}, Response: {r.text[:100]}")  # Log first 100 chars
            update.inline_query.answer([], switch_pm_text="Invalid response from Spotify. Try again.",
                                      switch_pm_parameter='jsonerror', cache_time=0)
            return

        if res['currently_playing_type'] == 'ad':
            update.inline_query.answer([], switch_pm_text="You're listening to ads.",
                                     switch_pm_parameter='ads', cache_time=0)
        elif res['currently_playing_type'] == 'track':
            username = is_user["username"]
            style = is_user["style"]
            image = drawImage(res, username, pfp, style)
            button = InlineKeyboardButton(
                text="Play on Spotify", url=res['item']['external_urls']['spotify'])
            temp = context.bot.send_photo(TEMP_CHANNEL, photo=image)
            photo = temp['photo'][1]['file_id']
            temp.delete()

            update.inline_query.answer(
                [
                    InlineQueryResultCachedPhoto(
                        id=uuid4(),
                        photo_file_id=photo,
                        reply_markup=InlineKeyboardMarkup([[button]])
                    )
                ], cache_time=0
            )
        else:
            update.inline_query.answer(
                [], switch_pm_text="Not sure what you're listening to.", switch_pm_parameter='notsure', cache_time=0)
    except Exception as ex:
        print(f"Error in inlineNowPlaying: {ex}")
        update.inline_query.answer([], switch_pm_text="You're not listening to anything.",
                                 switch_pm_parameter='notlistening', cache_time=0)


INLINE_QUERY_HANDLER = InlineQueryHandler(inlineNowPlaying)
dispatcher.add_handler(INLINE_QUERY_HANDLER)

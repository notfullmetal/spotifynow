import math
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO

from sp_bot.modules.misc import Fonts
from sp_bot import LOGGER


def get_text_width(text, font):
    """Get text width compatible with both old and new Pillow versions"""
    try:
        # For newer Pillow versions
        return font.getlength(text)
    except AttributeError:
        try:
            # For medium-new Pillow versions
            bbox = font.getbbox(text)
            if bbox is None or bbox[2] <= bbox[0]:
                # Fallback if getbbox returns None or invalid coordinates
                return len(text) * (font.size / 2)  # Rough approximation
            return bbox[2] - bbox[0]
        except AttributeError:
            # For older Pillow versions
            try:
                return font.getsize(text)[0]
            except Exception:
                # Final fallback
                return len(text) * (font.size / 2)  # Rough approximation


def truncate(text, font, limit):
    edited = True if get_text_width(text, font) > limit else False
    while get_text_width(text, font) > limit:
        text = text[:-1]
    if edited:
        return(text.strip() + '..')
    else:
        return(text.strip())


def checkUnicode(text):
    return text == str(text.encode('utf-8'))[2:-1]


def blurrImage(res, username, pfp, scrobbles):
    last_fm_temp_image = 'https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png'
    last_fm_logo = 'https://files.catbox.moe/098341.png'
    # last_fm_logo = 'https://files.catbox.moe/ymirt1.png'

    track = res.json()['recenttracks']['track'][0]

    artists = track['artist']['#text']
    albumname = track['album']['#text']
    songname = track['name']
    cover_url = track['image'][3]['#text']
    # coverart = 'https://files.catbox.moe/kux4sq.jpeg' if cover_url == '' or 'https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png' else cover_url
    coverart = cover_url
    if cover_url == '':
        coverart = last_fm_logo
    if cover_url == last_fm_temp_image:
        coverart = last_fm_logo

    song_url = track['url']
    tense = 'is' if '@attr' in track else 'was'

    # background object
    canvas = Image.new("RGB", (600, 250), (18, 18, 18))
    draw = ImageDraw.Draw(canvas, "RGBA")

    # album art
    try:
        # Create default art first as fallback (plain black with no text)
        default_art = Image.new("RGB", (200, 200), (18, 18, 18))
        # No text on the fallback image
        
        art = default_art  # Default in case all else fails
        
        # Try to get the image from URL
        link = coverart
        if link and link.startswith("http"):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            try:
                LOGGER.info(f"Fetching image from URL: {link}")
                r = requests.get(link, headers=headers, timeout=10)
                r.raise_for_status()  # Raise an exception for HTTP errors
                
                # Only continue if we got a valid content type
                content_type = r.headers.get('Content-Type', '')
                if 'image' in content_type:
                    try:
                        # Try to open the image
                        img_data = BytesIO(r.content)
                        img = Image.open(img_data)
                        
                        # Verify we can actually read the image data
                        img.verify()  # Verify it's a valid image
                        
                        # Reopen since verify() closed the file
                        img_data = BytesIO(r.content)
                        art = Image.open(img_data)
                        
                        # Resize it
                        art.thumbnail((200, 200), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                    except Exception as img_err:
                        LOGGER.exception(f"Error processing image data: {img_err}")
                else:
                    LOGGER.warning(f"Invalid content type for image: {content_type}")
            except Exception as req_err:
                LOGGER.exception(f"Error fetching image: {req_err}")
                
        # Create blurred background
        try:
            # Create a copy of the art for background
            bg = default_art.copy()  # Start with default
            if art != default_art:
                bg = art.copy()  # Use real art if available
                
            bg = bg.resize((600, 600))
            bg = bg.crop((0, 175, 600, 425))
            
            blurr = bg.filter(ImageFilter.GaussianBlur(radius=25))
            
            blurr_dark = ImageEnhance.Brightness(blurr)
            blurr_dark = blurr_dark.enhance(0.9)
            
            blurr_cont = ImageEnhance.Contrast(blurr_dark)
            blurr_cont = blurr_cont.enhance(0.8)
            
            canvas.paste(blurr_cont, (0, 0))
        except Exception as bg_err:
            LOGGER.exception(f"Error creating background: {bg_err}")
            # Just continue with default background
            
        # Paste the album art
        canvas.paste(art, (25, 25))
    except Exception as ex:
        LOGGER.exception(f"Fatal error in image processing: {ex}")
        # Canvas already has a default background so we'll continue with it

    # profile pic
    if pfp:
        try:
            # Try to open the image data
            profile_img_data = BytesIO(pfp.content)
            profile_img = Image.open(profile_img_data)
            
            # Verify we can actually read the image data
            profile_img.verify()
            
            # Reopen since verify() closed the file
            profile_img_data = BytesIO(pfp.content)
            profile_pic = Image.open(profile_img_data)
            
            # Resize it with proper error handling
            profile_pic.thumbnail((52, 52), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                
            canvas.paste(profile_pic, (523, 25))
        except Exception as e:
            LOGGER.exception(f"Error processing profile picture: {e}")
            # Continue without profile picture

    # set font sizes
    open_sans = ImageFont.truetype(Fonts.OPEN_SANS, 24)
    # open_bold = ImageFont.truetype(Fonts.OPEN_BOLD, 23)
    poppins = ImageFont.truetype(Fonts.POPPINS, 26)
    arial = ImageFont.truetype(Fonts.ARIAL, 26)
    arial23 = ImageFont.truetype(Fonts.ARIAL, 23)
    bold = ImageFont.truetype(Fonts.OPEN_BOLD, 22)

    # assign fonts
    songfont = poppins if checkUnicode(songname) else arial
    artistfont = open_sans if checkUnicode(artists) else arial23
    albumfont = open_sans if checkUnicode(albumname) else arial23

    # draw text on canvas
    white = '#ffffff'
    # draw.text((248, 18), truncate(username, poppins, 250),
    #           fill=white, font=poppins)
    # draw.text((248, 53), f"{tense} listening to",
    #           fill=white, font=open_sans)
    # draw.text((248, 132), truncate(songname, songfont, 315),
    #           fill=white, font=songfont)
    # draw.text((248, 167), truncate(artists, artistfont, 315),
    #           fill=white, font=artistfont)
    # draw.text((248, 197), truncate(albumname, albumfont, 315),
    #           fill=white, font=albumfont)

    '''
    draw.text((248, 18), truncate(username, poppins, 250),
              fill=white, font=poppins)
    draw.text((248, 53), f"{tense} listening to",
              fill=white, font=open_sans)
    draw.text((248, 115), truncate(songname, songfont, 315),
              fill=white, font=songfont)
    draw.text((248, 150), truncate(artists, artistfont, 315),
              fill=white, font=artistfont)
    draw.text((248, 180), truncate(albumname, albumfont, 315),
              fill=white, font=albumfont)

    '''
    try:
        draw.text((248, 18), truncate(username, poppins, 250),
                fill=white, font=poppins)
        draw.text((248, 53), f"{tense} listening to",
                fill=white, font=open_sans)
        draw.text((248, 105), truncate(songname, songfont, 315),
                fill=white, font=songfont)
        draw.text((248, 140), truncate(artists, artistfont, 315),
                fill=white, font=artistfont)
        draw.text((248, 170), truncate(albumname, albumfont, 315),
                fill=white, font=albumfont)
        draw.rectangle([(248, 221), (578, 223)], fill='#B3B3B3')
    except Exception as e:
        LOGGER.exception(f"Error drawing text: {e}")
        # Draw simplified text as fallback
        fallback_font = ImageFont.truetype(Fonts.ARIAL, 24)
        try:
            draw.text((248, 18), username[:20], fill=white, font=fallback_font)
            draw.text((248, 53), f"{tense} listening to", fill=white, font=fallback_font)
            draw.text((248, 105), songname[:30], fill=white, font=fallback_font)
            draw.text((248, 140), artists[:30], fill=white, font=fallback_font)
            draw.text((248, 170), albumname[:30], fill=white, font=fallback_font)
            draw.rectangle([(248, 221), (578, 223)], fill='#B3B3B3')
        except Exception as e2:
            LOGGER.exception(f"Fallback text drawing also failed: {e2}")

    if scrobbles != "off":
        try:
            w = {1: 45, 2: 58, 3: 73, 4: 86, 5: 100, 6: 111}[len(scrobbles)]
            draw.rounded_rectangle([(18, 200), (w, 230)],
                                radius=13, fill='#121212')
            draw.text((26, 200), scrobbles, fill='#ffffff', font=bold)
        except Exception as e:
            LOGGER.exception(f"Error drawing scrobbles: {e}")

    # return canvas
    image = BytesIO()
    canvas.save(image, 'JPEG', quality=200)
    image.seek(0)
    return image

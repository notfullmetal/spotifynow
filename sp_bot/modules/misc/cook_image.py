import math
import logging
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO

from sp_bot.modules.misc import Fonts

logger = logging.getLogger(__name__)


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


def fetch_image(url, timeout=10):
    """Safely fetch an image from a URL and return a PIL Image object or None on failure"""
    if not url or not url.startswith("http"):
        logger.error(f"Invalid image URL: {url}")
        return None
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        logger.info(f"Fetching image from URL: {url}")
        r = requests.get(url, headers=headers, timeout=timeout)
        
        if r.status_code != 200:
            logger.error(f"HTTP error when fetching image: {r.status_code}")
            return None
            
        content_type = r.headers.get('Content-Type', '')
        if 'image' not in content_type:
            logger.error(f"Invalid content type for image: {content_type}")
            return None
            
        img_data = BytesIO(r.content)
        image = Image.open(img_data)
        
        # Just access the format to ensure the image is valid (will raise an exception if not)
        _ = image.format
        
        return image
    except requests.RequestException as e:
        logger.error(f"Request exception when fetching image: {e}")
        return None
    except Exception as e:
        logger.error(f"General exception when fetching image: {e}")
        return None


def drawImage(res, username, pfp, style):
    try:
        songname = res['item']['name']
        albumname = res['item']['album']['name']
        totaltime = res['item']['duration_ms']
        currtime = res['progress_ms']
        coverart = res['item']['album']['images'][1]['url']
        song_url = res['item']['external_urls']['spotify']
        artists = ', '.join([x['name']
                            for x in res['item']['artists']])
    except Exception as e:
        logger.error(f"Error extracting song data: {e}")
        # Create a basic error image with text
        canvas = Image.new("RGB", (600, 250), (18, 18, 18))
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype(Fonts.ARIAL, 24)
            draw.text((50, 100), "Error displaying song info", fill='#ffffff', font=font)
        except Exception:
            pass  # Even the error display failed
        
        image = BytesIO()
        canvas.save(image, 'JPEG', quality=95)
        image.seek(0)
        return image

    # background object
    canvas = Image.new("RGB", (600, 250), (18, 18, 18))
    draw = ImageDraw.Draw(canvas)

    # album art
    try:
        # Create default art first as fallback (plain black with no text)
        default_art = Image.new("RGB", (200, 200), (18, 18, 18))
        # Use default art as starting point
        art = default_art
        
        # Try to get the image from URL using our safer function
        album_image = fetch_image(coverart)
        if album_image:
            # Resize it
            album_image.thumbnail((200, 200), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
            art = album_image

        # Create blurred background if needed
        if style == "blur":
            try:
                # Create a copy of the art for background
                bg = art.copy()
                bg = bg.resize((600, 600))
                bg = bg.crop((0, 175, 600, 425))
                
                blurr = bg.filter(ImageFilter.GaussianBlur(radius=25))
                
                blurr_dark = ImageEnhance.Brightness(blurr)
                blurr_dark = blurr_dark.enhance(0.9)
                
                blurr_cont = ImageEnhance.Contrast(blurr_dark)
                blurr_cont = blurr_cont.enhance(0.8)
                
                canvas.paste(blurr_cont, (0, 0))
            except Exception as bg_err:
                logger.error(f"Error creating background: {bg_err}")
                # Just continue with default background
                
        # Paste the album art
        canvas.paste(art, (25, 25))
    except Exception as ex:
        logger.error(f"Fatal error in image processing: {ex}")
        # Canvas already has a default background so we'll continue with it

    # profile pic
    if pfp:
        try:
            profile_img_data = BytesIO(pfp.content)
            profile_pic = Image.open(profile_img_data)
            
            # Just access the format to ensure the image is valid
            _ = profile_pic.format
            
            # Resize it with proper error handling
            profile_pic.thumbnail((52, 52), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                
            canvas.paste(profile_pic, (523, 25))
        except Exception as e:
            logger.error(f"Error processing profile picture: {e}")
            # Continue without profile picture

    # set font sizes
    open_sans = ImageFont.truetype(Fonts.OPEN_SANS, 24)
    # open_bold = ImageFont.truetype(Fonts.OPEN_BOLD, 23)
    poppins = ImageFont.truetype(Fonts.POPPINS, 26)
    arial = ImageFont.truetype(Fonts.ARIAL, 26)
    arial23 = ImageFont.truetype(Fonts.ARIAL, 23)

    # assign fonts
    songfont = poppins if checkUnicode(songname) else arial
    artistfont = open_sans if checkUnicode(artists) else arial23
    albumfont = open_sans if checkUnicode(albumname) else arial23

    # draw text on canvas
    white = '#ffffff'
    try:
        draw.text((248, 18), truncate(username, poppins, 250),
                fill=white, font=poppins)
        draw.text((248, 53), "is listening to",
                fill=white, font=open_sans)
        draw.text((248, 115), truncate(songname, songfont, 315),
                fill=white, font=songfont)
        draw.text((248, 150), truncate(artists, artistfont, 315),
                fill=white, font=artistfont)
        draw.text((248, 180), truncate(albumname, albumfont, 315),
                fill=white, font=albumfont)
    except Exception as e:
        logger.error(f"Error drawing text: {e}")
        # Draw simplified text as fallback
        fallback_font = ImageFont.truetype(Fonts.ARIAL, 24)
        try:
            draw.text((248, 18), username[:20], fill=white, font=fallback_font)
            draw.text((248, 53), "is listening to", fill=white, font=fallback_font)
            draw.text((248, 115), songname[:30], fill=white, font=fallback_font)
            draw.text((248, 150), artists[:30], fill=white, font=fallback_font)
            draw.text((248, 180), albumname[:30], fill=white, font=fallback_font)
        except Exception as e2:
            logger.error(f"Fallback text drawing also failed: {e2}")

    # draw progress bar on canvas
    try:
        # Sanity check on progress values
        if totaltime > 0 and currtime >= 0 and currtime <= totaltime:
            progress_width = currtime / totaltime * 330
            # Ensure the progress width is valid (at least 1 pixel)
            progress_width = max(1, progress_width)
            
            # Background bar (correct coordinate order: x0, y0, x1, y1)
            draw.rectangle([(248, 222), (578, 224)], fill='#404040')
            
            # Progress bar (ensure coordinates are in correct order)
            x0 = 248
            x1 = 248 + progress_width
            if x1 > x0:
                draw.rectangle([(x0, 222), (x1, 224)], fill='#B3B3B3')
        else:
            # Draw empty bar for invalid progress values
            draw.rectangle([(248, 222), (578, 224)], fill='#404040')
    except Exception as e:
        logger.error(f"Error drawing progress bar: {e}")
        # Draw a simple empty bar as fallback
        try:
            draw.rectangle([(248, 222), (578, 224)], fill='#404040')
        except Exception:
            logger.error("Failed to draw even the fallback progress bar")

    # return canvas
    image = BytesIO()
    canvas.save(image, 'JPEG', quality=95)  # Reduced quality to avoid large images
    image.seek(0)
    return image

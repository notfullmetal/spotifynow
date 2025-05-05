import requests
import json
import logging
from sp_bot import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

logger = logging.getLogger(__name__)

class SpotifyUser:
    authorize_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        logger.info(f"Initialized SpotifyUser with redirect URI: {redirect_uri}")

    def getAuthUrl(self):
        """
        Get the authorization URL for the user to authorize the application
        This will redirect to the Cloudflare Worker after Spotify auth
        """
        authorization_redirect_url = self.authorize_url + '?response_type=code&client_id=' + \
            self.client_id + '&redirect_uri=' + self.redirect_uri + \
            '&scope=user-read-currently-playing'
        return authorization_redirect_url

    def getAccessToken(self, authCode):
        """
        Get an access token using the authorization code
        """
        if not authCode:
            logger.error("Auth code is None or empty")
            return 'error'
            
        data = {'grant_type': 'authorization_code',
                'code': authCode, 'redirect_uri': self.redirect_uri}
        
        try:
            r = requests.post(
                self.token_url, data=data, allow_redirects=True, auth=(self.client_id, self.client_secret))

            if r.status_code in range(200, 299):
                res = json.loads(r.text)
                return res['refresh_token']
            else:
                logger.error(f"Error getting access token: {r.status_code}, {r.text}")
                return 'error'
        except Exception as e:
            logger.error(f"Exception getting access token: {e}")
            return 'error'

    def getCurrentyPlayingSong(self, refreshToken):
        """
        Get the currently playing song for a user using their refresh token
        
        Returns:
            requests.Response: The response object from the Spotify API call
            None: If the request fails or the token is invalid
        """
        if not refreshToken or refreshToken == '00000':
            logger.error("Invalid refresh token")
            return None
            
        try:
            # First, get a new access token using the refresh token
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refreshToken,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            token_response = requests.post(self.token_url, data=data, timeout=10)
            
            if token_response.status_code != 200:
                logger.error(f"Error refreshing token: {token_response.status_code}, {token_response.text}")
                return None
            
            # Validate the token response
            try:
                token = token_response.json()
                if 'access_token' not in token:
                    logger.error(f"Token response missing access_token: {token_response.text[:100]}")
                    return None
            except json.JSONDecodeError:
                logger.error(f"Failed to parse token response as JSON: {token_response.text[:100]}")
                return None

            # Make the request to get currently playing song
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {token['access_token']}"
            }
            
            current_song_url = 'https://api.spotify.com/v1/me/player/currently-playing'
            r = requests.get(current_song_url, headers=headers, timeout=10)
            
            # Handle common response status codes
            if r.status_code == 204:
                logger.info("User is not currently playing anything")
                # Return the response with 204 status so the caller can handle this case
                return r
            elif r.status_code == 401:
                logger.error("Unauthorized - token may be invalid")
                return None
            elif r.status_code == 429:
                logger.error("Rate limited by Spotify API")
                return None
            elif r.status_code != 200:
                logger.error(f"API error: {r.status_code}")
                return None

            # Validate that we got a valid JSON response
            if not r.text:
                logger.error("Empty response from Spotify API")
                return None
                
            # Try to parse as JSON to validate, but don't store the result
            # This will raise JSONDecodeError if invalid
            _ = r.json()
                
            return r
            
        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to Spotify API")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error with Spotify API")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Exception getting currently playing song: {e}")
            return None


SPOTIFY = SpotifyUser(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

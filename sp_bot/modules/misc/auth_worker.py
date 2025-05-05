import requests
import json
import logging

from sp_bot import config, JSON_BLOB_ID

logger = logging.getLogger(__name__)

class CloudflareAuth:
    """
    Class to handle authentication with Cloudflare Worker.
    The Cloudflare Worker stores auth codes in a JSON blob and redirects to Telegram with a key.
    """
    def __init__(self, json_blob_url=None):
        # Use the provided URL or construct it from the config
        if json_blob_url:
            self.json_blob_url = json_blob_url
        else:
            self.json_blob_url = f"https://jsonblob.com/api/{JSON_BLOB_ID}"
            
        logger.info(f"Initialized CloudflareAuth with JSON Blob URL: {self.json_blob_url}")
    
    def fetch_auth_code(self, key):
        """
        Fetch the authentication code from the JSON blob using the key
        """
        try:
            response = requests.get(self.json_blob_url)
            if response.status_code == 200:
                data = response.json()
                # Extract the auth code using the key
                auth_code = data.get(key)
                if auth_code:
                    # Clean up the entry after retrieving it
                    self._cleanup_key(key, data)
                return auth_code
            else:
                logger.error(f"Failed to fetch auth code. Status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching auth code: {e}")
            return None
    
    def _cleanup_key(self, key, data):
        """
        Remove the key-value pair from the JSON blob after it's been used
        """
        try:
            if key in data:
                del data[key]
                requests.put(
                    self.json_blob_url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(data)
                )
        except Exception as e:
            logger.error(f"Error cleaning up key: {e}")

# Initialize the CloudflareAuth instance with the configuration
CLOUDFLARE_AUTH = CloudflareAuth() 
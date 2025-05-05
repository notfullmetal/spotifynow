import os


class Config:
    # Class variables (accessible as Config.VARIABLE)
    API_KEY = os.getenv('API_KEY')
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    MONGO_USR = os.getenv('MONGO_USR')
    MONGO_PASS = os.getenv('MONGO_PASS')
    MONGO_COLL = os.getenv('MONGO_COLL')
    TEMP_CHANNEL = os.getenv('TEMP_CHANNEL')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
    JSON_BLOB_ID = os.getenv('JSON_BLOB_ID')
    
    # PostgreSQL Configuration
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    
    def __init__(self):
        # Instance variables (accessible via instance.VARIABLE)
        # These copy class variables to instance variables for database ops
        self.POSTGRES_USER = Config.POSTGRES_USER
        self.POSTGRES_PASSWORD = Config.POSTGRES_PASSWORD
        self.POSTGRES_HOST = Config.POSTGRES_HOST
        self.POSTGRES_PORT = Config.POSTGRES_PORT
        self.POSTGRES_DB = Config.POSTGRES_DB
        self.JSON_BLOB_ID = Config.JSON_BLOB_ID
    
    # Database URL for SQLAlchemy
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # JSON Blob URL
    @property
    def JSON_BLOB_URL(self):
        return f"https://jsonblob.com/api/{self.JSON_BLOB_ID}"

from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Code(Base):
    """Temporary authentication codes"""
    __tablename__ = 'codes'
    
    id = Column(String, primary_key=True)
    auth_code = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Code(id='{self.id}', auth_code='{self.auth_code}')>"

class User(Base):
    """Spotify user data"""
    __tablename__ = 'users'
    
    tg_id = Column(String, primary_key=True)
    username = Column(String, nullable=False, default="User")
    token = Column(String, nullable=False)
    style = Column(String, nullable=False, default="blur")
    
    def __repr__(self):
        return f"<User(tg_id='{self.tg_id}', username='{self.username}', style='{self.style}')>"

class LastFMUser(Base):
    """LastFM user data"""
    __tablename__ = 'lastfm'
    
    tg_id = Column(String, primary_key=True)
    fm_username = Column(String, nullable=False)
    name = Column(String, nullable=False, default="User")
    counter = Column(String, nullable=False, default="on")
    
    def __repr__(self):
        return f"<LastFMUser(tg_id='{self.tg_id}', fm_username='{self.fm_username}', name='{self.name}')>" 
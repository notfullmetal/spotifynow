from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import uuid

from sp_bot import config
from sp_bot.modules.db.models import Base, Code, User, LastFMUser


class PostgresOperations:
    def __init__(self, config_obj):
        # Create database engine
        database_url = f"postgresql://{config_obj.POSTGRES_USER}:{config_obj.POSTGRES_PASSWORD}@{config_obj.POSTGRES_HOST}:{config_obj.POSTGRES_PORT}/{config_obj.POSTGRES_DB}"
        self.engine = create_engine(database_url)
        
        # Create all tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create a session factory
        self.Session = sessionmaker(bind=self.engine)
    
    # 'Codes' database functions

    def fetchCode(self, _id):
        session = self.Session()
        try:
            code = session.query(Code).filter_by(id=str(_id)).first()
            return {"_id": code.id, "authCode": code.auth_code} if code else None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def deleteCode(self, _id):
        session = self.Session()
        try:
            code = session.query(Code).filter_by(id=str(_id)).first()
            if code:
                session.delete(code)
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def addCode(self, auth_code):
        session = self.Session()
        try:
            code_id = str(uuid.uuid4())
            new_code = Code(id=code_id, auth_code=auth_code)
            session.add(new_code)
            session.commit()
            return code_id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    # 'Users' database functions

    def fetchData(self, tg_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            if user:
                return {
                    "tg_id": user.tg_id,
                    "username": user.username,
                    "token": user.token,
                    "style": user.style
                }
            return None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def updateData(self, tg_id, value):
        session = self.Session()
        try:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            if user:
                user.username = value
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def updateStyle(self, tg_id, value):
        session = self.Session()
        try:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            if user:
                user.style = value
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def deleteData(self, tg_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            if user:
                session.delete(user)
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def countAll(self):
        session = self.Session()
        try:
            return session.query(User).count()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return 0
        finally:
            session.close()

    def aggregateUsers(self):
        session = self.Session()
        try:
            # Group by style and count
            from sqlalchemy import func
            result = session.query(User.style, func.count(User.style)).group_by(User.style).all()
            return [{"_id": style, "count": count} for style, count in result]
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            session.close()

    def addUser(self, tg_id, token):
        session = self.Session()
        try:
            new_user = User(
                tg_id=tg_id,
                username="User",
                token=token,
                style="blur"
            )
            session.add(new_user)
            session.commit()
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    # 'LastFM' database functions

    def addLastFmUser(self, tg_id, lastfm_username):
        session = self.Session()
        try:
            new_user = LastFMUser(
                tg_id=tg_id,
                fm_username=lastfm_username,
                name="User",
                counter="on"
            )
            session.add(new_user)
            session.commit()
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def getLastFmUser(self, tg_id):
        session = self.Session()
        try:
            user = session.query(LastFMUser).filter_by(tg_id=tg_id).first()
            if user:
                return {
                    "tg_id": user.tg_id,
                    "fm_username": user.fm_username,
                    "name": user.name,
                    "counter": user.counter
                }
            return None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            session.close()

    def updateLastFmData(self, tg_id, value):
        session = self.Session()
        try:
            user = session.query(LastFMUser).filter_by(tg_id=tg_id).first()
            if user:
                user.name = value
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def removeLastFmUser(self, tg_id):
        session = self.Session()
        try:
            user = session.query(LastFMUser).filter_by(tg_id=tg_id).first()
            if user:
                session.delete(user)
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()

    def countAllLastFm(self):
        session = self.Session()
        try:
            return session.query(LastFMUser).count()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return 0
        finally:
            session.close()

    def aggregateLastFmUsers(self):
        session = self.Session()
        try:
            # Group by counter and count
            from sqlalchemy import func
            result = session.query(LastFMUser.counter, func.count(LastFMUser.counter)).group_by(LastFMUser.counter).all()
            return [{"_id": counter, "count": count} for counter, count in result]
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            session.close()

    def toggleCounter(self, tg_id, value):
        session = self.Session()
        try:
            user = session.query(LastFMUser).filter_by(tg_id=tg_id).first()
            if user:
                user.counter = value
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()


# Initialize the database with the config instance
DATABASE = PostgresOperations(config)

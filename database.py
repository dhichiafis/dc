from sqlalchemy.orm import sessionmaker,declarative_base

from sqlalchemy import create_engine

from config import *
Base=declarative_base()


DB_URL=settings.DB_URL

engine=create_engine(url=DB_URL)

SessionFactory=sessionmaker(autoflush=False,autocommit=False,bind=engine)


def connect():
    db=SessionFactory()
    try:
        yield db 

    finally:
        db.close()
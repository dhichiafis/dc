from sqlalchemy import Column,Integer,ForeignKey,String 
from datetime import datetime
from database import *
class User(Base):

    __tablename__='users'
    id=Column('id',Integer,primary_key=True)
    username=Column('username',String)
    password=Column('password',String)


    
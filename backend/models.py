from .db import Base
from sqlalchemy import String, Integer, Column, Float, ForeignKey

class user(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=True) 
    password = Column(String) 

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    image_path = Column(String,nullable=True)
    name = Column(String,nullable=False)
    height = Column(Float,nullable=False)
    weight = Column(Float,nullable=False)
    fights = Column(Integer,nullable=True)
    wins = Column(Integer,nullable=True)
    losses = Column(Integer,nullable=True)
    draws = Column(Integer,nullable=True)


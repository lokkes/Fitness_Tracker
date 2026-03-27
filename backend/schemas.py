from pydantic import BaseModel
from .models import UserInfo

class CreateUser(BaseModel):
    name: str         
    email: str         
    password: str  

class UserLogin(BaseModel):
    email: str         
    password: str 

class PersonalInfo(BaseModel):
    email:str
    name:str
    height:float
    weight:float
    fights:int
    wins:int
    losses:int
    draws:int

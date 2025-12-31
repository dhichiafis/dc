from pydantic import BaseModel

class UserBase(BaseModel):
    id:int 
    username:str 

class UserCreate(BaseModel):
    username:str 
    password:str 
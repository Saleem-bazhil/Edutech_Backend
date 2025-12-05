from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    email:EmailStr
    password: str
    
class Token(BaseModel):
    access_tooken = str
    token_type: str ="bearer"
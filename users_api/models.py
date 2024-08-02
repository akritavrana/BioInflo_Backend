from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    username: str

class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str

    class Config:
        from_attributes = True
        
class UserInDB(BaseModel):
    username: str
    password: str

class UserEdit(BaseModel):
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str 

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

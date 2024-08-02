from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from pymongo.database import Database

from db import get_db
from .models import UserCreate, UserResponse,Token, UserEdit, ChangePassword
from .schema import create_user, get_user, get_user_by_email, edit_user, delete_user
from .auth import verify_password,get_password_hash, create_access_token, authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES


users_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


@users_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.post("/create-user", response_model=UserResponse)
async def create_new_user(user: UserCreate, db: Database = Depends(get_db)):
    # Check if username already exists
    existing_user_by_username = await get_user(db, username=user.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_user_by_email = await get_user_by_email(db, email=user.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password and create the user
    user.password = get_password_hash(user.password)
    created_user = await create_user(db, user)
    return created_user

@users_router.get("/me", response_model=UserResponse)
async def read_users_me(token: str = Depends(oauth2_scheme),db: Database = Depends(get_db)):
    return await get_current_user(token=token,db=db)

@users_router.patch("/edit-user", response_model=UserResponse)
async def update_user(
    user: UserEdit,
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db)
):
    current_user = await get_current_user(token=token,db=db)
    updated_user = await edit_user(db, current_user['username'], user.model_dump(exclude_unset=True))
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@users_router.delete("/delete-user", response_model=dict)
async def remove_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db)
):
    current_user = await get_current_user(token=token,db=db)
    deleted_count = await delete_user(db, current_user['username'])
    if deleted_count:
        return {"detail": "User has been successfully deleted"}
    raise HTTPException(status_code=404, detail="User not found")

@users_router.patch('/change-password',response_model=UserResponse)
async def change_passsword(
    changepassword:ChangePassword,
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
):
    current_user = await get_current_user(token=token,db=db)
    if not verify_password(changepassword.old_password,current_user['hashed_password']):
        raise HTTPException(status_code=404, detail="Password Incorrect")
    password_dict = {
        'hashed_password' : get_password_hash(changepassword.new_password)
    }
    updated_user = await edit_user(db, current_user['username'], password_dict)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")

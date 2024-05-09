from fastapi import APIRouter, HTTPException, status, Depends
from fastapi import BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models_and_utils import UserInDB, users_collection, get_password_hash, verify_password, create_access_token, send_recovery_email, SECRET_KEY, ALGORITHM
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets

# OAuth2 scheme for bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# FastAPI router for authentication endpoints
auth_router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: str

class UserResetPassword(BaseModel):
    password: str

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PerformPasswordReset(BaseModel):
    email: EmailStr
    recovery_code: str
    new_password: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_data = users_collection.find_one({"username": username})
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserInDB(**user_data)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

@auth_router.post("/register")
async def register_user(user: UserCreate):
    if users_collection.find_one({"username": user.username}) or users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({"username": user.username, "email": user.email, "password": hashed_password})
    return {"message": "User registered successfully."}

@auth_router.post("/login")
async def login_user(user: UserLogin):
    # Check both username and email, prioritize username if provided
    user_data = None
    if user.username:
        user_data = users_collection.find_one({"username": user.username})
    elif user.email:
        user_data = users_collection.find_one({"email": user.email})
    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username, email, or password.")
    
    access_token = create_access_token(data=user_data["username"])
    return {"access_token": access_token, "token_type": "bearer"}



@auth_router.post("/request_reset")
async def request_password_reset(request: PasswordRecoveryRequest, background_tasks: BackgroundTasks):
    user_data = users_collection.find_one({"email": request.email})
    if not user_data:
        raise HTTPException(status_code=404, detail="No user found with this email.")

    recovery_code = secrets.token_urlsafe(16)
    users_collection.update_one({"email": request.email}, {"$set": {"recovery_code": recovery_code}})
    background_tasks.add_task(send_recovery_email, request.email, recovery_code)

    return {"message": "Recovery code sent to your email. Please check your inbox."}


@auth_router.post("/perform_reset")
async def perform_password_reset(reset: PerformPasswordReset):
    user_data = users_collection.find_one({"email": reset.email, "recovery_code": reset.recovery_code})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid recovery code or email.")
    
    new_password_hash = get_password_hash(reset.new_password)
    users_collection.update_one({"email": reset.email}, {"$set": {"password": new_password_hash, "recovery_code": None}})
    return {"message": "Password has been successfully reset."}

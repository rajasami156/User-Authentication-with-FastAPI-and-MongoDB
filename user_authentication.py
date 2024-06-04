from fastapi import APIRouter, HTTPException, status, Depends
from fastapi import BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models_and_utils import UserInDB, users_collection, get_password_hash, verify_password, create_access_token, send_recovery_email, send_welcome_email, SECRET_KEY, ALGORITHM
from pydantic import BaseModel, EmailStr
import secrets

# OAuth2 scheme for bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# FastAPI router for authentication endpoints
auth_router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResetPassword(BaseModel):
    password: str

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class VerifyRecoveryCode(BaseModel):
    recovery_code: str

class SetNewPassword(BaseModel):
    token: str
    new_password: str
    confirm_password: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_data = users_collection.find_one({"email": email})
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserInDB(**user_data)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

@auth_router.post("/register")
async def register_user(user: UserCreate, background_tasks: BackgroundTasks):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists.")
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({"email": user.email, "password": hashed_password, "username": user.username})  # Include username
    background_tasks.add_task(send_welcome_email, user.email)
    return {"message": "User registered successfully."}

@auth_router.post("/login")
async def login_user(user: UserLogin):
    user_data = users_collection.find_one({"email": user.email})
    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    
    access_token = create_access_token(data={"sub": user_data["email"]})
    # Fetch the username from user_data, ensuring to handle cases where it might not exist
    username = user_data.get("username", "No username set")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "username": username  # Include the username in the response
    }

@auth_router.post("/request_reset")
async def request_password_reset(request: PasswordRecoveryRequest, background_tasks: BackgroundTasks):
    user_data = users_collection.find_one({"email": request.email})
    if not user_data:
        raise HTTPException(status_code=404, detail="No user found with this email.")

    recovery_code = secrets.token_urlsafe(16)
    users_collection.update_one({"email": request.email}, {"$set": {"recovery_code": recovery_code}})
    background_tasks.add_task(send_recovery_email, request.email, recovery_code)

    return {"message": "Recovery code sent to your email. Please check your inbox."}

@auth_router.post("/verify_code")
async def verify_recovery_code(data: VerifyRecoveryCode):
    user_data = users_collection.find_one({"recovery_code": data.recovery_code})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid recovery code.")
    
    # Create a temporary JWT token with user's email for the next step
    token_data = {"sub": user_data["email"]}
    temp_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"token": temp_token}

@auth_router.post("/set_new_password")
async def set_new_password(data: SetNewPassword):
    try:
        # Decode and validate the temporary token
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token.")
    
    # Ensure that both passwords match
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    
    # Update the user's password and clear the recovery code
    new_password_hash = get_password_hash(data.new_password)
    users_collection.update_one(
        {"email": user_email},
        {"$set": {"password": new_password_hash, "recovery_code": None}},
    )
    
    return {"message": "Password has been successfully reset."}

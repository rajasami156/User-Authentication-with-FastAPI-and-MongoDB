from pymongo import MongoClient
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from aiosmtplib import SMTP
import asyncio
import smtplib
from email.message import EmailMessage

load_dotenv()

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["Api"]
users_collection = db["UserAuthentication"]

# SMTP settings
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_MAIL_DEFAULT_SENDER = os.getenv("SMTP_MAIL_DEFAULT_SENDER")
SMTP_MAIL_USE_SSL = True

# JWT and security settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserInDB(BaseModel):
    username: str
    password: str
    email: str = None  # Optional: add if storing emails in your user schema

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": data, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def send_recovery_email(email: str, recovery_code: str):
    message = EmailMessage()
    message["From"] = SMTP_MAIL_DEFAULT_SENDER
    message["To"] = email
    message["Subject"] = "Password Recovery Code"
    message.set_content(f"Your password recovery code is: {recovery_code}")

    try:
        with smtplib.SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT) as smtp:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(message)
            return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"
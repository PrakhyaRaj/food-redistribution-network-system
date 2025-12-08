# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env from backend folder

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # PostgreSQL URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 30 * 60  # 30 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7 days
    JWT_BLOCKLIST = set()  # in-memory token blocklist

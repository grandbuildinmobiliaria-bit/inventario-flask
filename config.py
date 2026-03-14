import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 180
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

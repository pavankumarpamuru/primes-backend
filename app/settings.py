import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Primes Backend")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./primes.db")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "AHFKADUSHFAKSHDFASIUOHFASDFAKJHASDFU")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "3600"))

PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

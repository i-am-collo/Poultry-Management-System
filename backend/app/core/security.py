from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os

from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
DEV_FALLBACK_SECRET_KEY = "dev-insecure-secret-change-me"
SECRET_KEY = os.getenv("SECRET_KEY", "").strip() or DEV_FALLBACK_SECRET_KEY

if APP_ENV in {"production", "staging"} and SECRET_KEY == DEV_FALLBACK_SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set for production or staging environments.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "60"))
MAX_BCRYPT_PASSWORD_BYTES = 72


def _is_password_too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES


def hash_password(password: str) -> str:
    if _is_password_too_long(password):
        raise ValueError(f"Password exceeds {MAX_BCRYPT_PASSWORD_BYTES} bytes when UTF-8 encoded")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _is_password_too_long(plain_password):
        return False
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_in_minutes: int) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(email: str, role: str) -> str:
    return _create_token(
        {"sub": email, "role": role, "type": "access"},
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_reset_token(email: str) -> str:
    return _create_token(
        {"sub": email, "type": "reset"},
        RESET_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(email: str) -> str:
    """Generate refresh token (7 days expiry by default)"""
    payload = {
        "sub": email,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_refresh_token(token: str) -> dict:
    """Validate refresh token and return decoded payload"""
    from jose import JWTError
    try:
        decoded = decode_token(token)
        if decoded.get("type") != "refresh":
            raise ValueError("Invalid token type")
        return decoded
    except JWTError:
        raise ValueError("Invalid or expired refresh token")

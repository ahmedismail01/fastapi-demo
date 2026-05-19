from datetime import timedelta, datetime
from passlib.hash import bcrypt
from jwt import decode, encode
from core.config import dotenv_config

access_token_expire_minutes = dotenv_config.get("access_token_expire_minutes")
secret_key = dotenv_config.get("secret_key")
algorithm = dotenv_config.get("algorithm")


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return encode(to_encode, secret_key, algorithm=algorithm)


def verify_access_token(token):
    return decode(token, key=secret_key, algorithms=[algorithm])

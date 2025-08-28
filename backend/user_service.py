import hashlib
import secrets
import time
from typing import Dict, Optional, Union


# 模拟数据库存储
users_db: Dict[str, dict] = {}
verification_codes: Dict[str, Dict[str, Union[str, float]]] = {}  # email -> {code, timestamp}


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password with a salt.
    Returns tuple of (hashed_password, salt).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex(), salt


def verify_password(stored_password_hash: str, salt: str, provided_password: str) -> bool:
    """
    Verify a stored password hash against one provided by user
    """
    pwdhash, _ = hash_password(provided_password, salt)
    return pwdhash == stored_password_hash


def create_user(email: str, password: str) -> dict:
    """
    Create a new user
    """
    # Check if user already exists
    if email in users_db:
        raise ValueError("User with this email already exists")

    # Hash password
    password_hash, salt = hash_password(password)
    
    user = {
        "email": email,
        "password_hash": password_hash + ":" + salt  # Store both hash and salt
    }
    
    users_db[email] = user
    return user


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email
    """
    return users_db.get(email)


def authenticate_user(email: str, password: str) -> Optional[bool]:
    """
    Authenticate user and return token if successful
    """
    user = users_db.get(email)
    if not user:
        return None

    # Extract hash and salt
    stored_password_hash, salt = user["password_hash"].split(":")

    # Verify password
    if not verify_password(stored_password_hash, salt, password):
        return None

    return True


def store_verification_code(email: str, code: str):
    """
    Store verification code for an email
    """
    verification_codes[email] = {
        "code": code,
        "timestamp": time.time()
    }


def verify_code(email: str, code: str) -> bool:
    """
    Verify if the code for an email is valid and not expired
    """
    if email not in verification_codes:
        return False

    stored_data = verification_codes[email]
    # Check if code matches and is not older than 10 minutes
    if stored_data["code"] == code and (time.time() - stored_data["timestamp"]) < 600:
        return True
    return False


def delete_verification_code(email: str):
    """
    Delete verification code after successful use
    """
    if email in verification_codes:
        del verification_codes[email]
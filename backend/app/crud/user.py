import hashlib
import secrets
from typing import Optional
from backend.app.models.user import UserTable, UserLogin, User
from sqlmodel import Session, select


class UserCRUD:
    @staticmethod
    def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        """
        Hash a password with a salt.
        Returns tuple of (hashed_password, salt).
        """
        if salt is None:
            salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwdhash.hex(), salt
    
    @staticmethod
    def verify_password(stored_password_hash: str, salt: str, provided_password: str) -> bool:
        """
        Verify a stored password hash against one provided by user
        """
        pwdhash, _ = UserCRUD.hash_password(provided_password, salt)
        return pwdhash == stored_password_hash

    @staticmethod
    def create_user(db: Session, phone: str) -> User:
        user = UserTable(phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[UserTable]:
        """
        根据手机号查询用户
        """
        statement = select(UserTable).where(UserTable.phone == phone)
        return db.exec(statement).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[UserTable]:
        """
        根据ID查询用户
        """
        statement = select(UserTable).where(UserTable.id == user_id)
        return db.exec(statement).first()

    @staticmethod
    def authenticate_user(db: Session, phone: str, password: str) -> Optional[UserTable]:
        """
        验证用户身份
        """
        user = UserCRUD.get_user_by_phone(db, phone)
        if not user:
            return None
        
        # 分离存储的哈希和盐
        stored_hash, salt = user.password_hash.split(':', 1)
        if UserCRUD.verify_password(stored_hash, salt, password):
            return user
        return None
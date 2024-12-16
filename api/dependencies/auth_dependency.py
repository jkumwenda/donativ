import os
import string
import secrets
from typing import Annotated
from starlette import status
from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.hash import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.models import User, Role, User, RolePermission, UserRole, Permission

load_dotenv()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


class Auth:
    def __init__(self, db: Session):
        self.db = db

    def create_access_token(self, username, user_id, expires_delta: timedelta):
        encode = {"sub": username, "id": user_id}
        expires = datetime.now() + expires_delta
        encode["exp"] = expires
        return jwt.encode(encode, os.getenv("SECRET_KEY", ""), algorithm=os.getenv("ALGORITHM", ""))

    def authenticate_user(self, email, password):
        user = self.db.query(User).filter(User.email == email).first()
        if user and bcrypt.verify(password, user.hashed_password):
            return user
        return user if user and bcrypt.verify(password, user.hashed_password) else None

    def check_existing_user(self, email, phone):
        if (self.db.query(User).filter(User.email == email).first()):
            raise HTTPException(status_code=400, detail="Email already exists")

        if (self.db.query(User).filter(User.phone == phone).first()):
            raise HTTPException(
                status_code=400, detail="Phone number already exists")

    def get_user_role(self, role_name: str):
        role = self.db.query(Role).filter(Role.role == role_name).first()
        if role is None:
            raise HTTPException(
                status_code=404, detail="Role does not exist")
        return role

    def generate_random_password(self, length=12):
        if length < 12:
            raise ValueError(
                "Password length should be at least 12 characters")
        return "".join(
            secrets.choice(string.ascii_letters +
                           string.digits + string.punctuation)
            for _ in range(length)
        )

    def hash_password(self, password):
        return bcrypt.hash(password)

    def secure_access(self, permission_code, user_id):
        permission = self.db.query(UserRole, User, RolePermission, Permission).filter(
            User.id == UserRole.user_id, User.id == user_id).filter(
            UserRole.role_id == RolePermission.role_id).filter(
            Permission.id == RolePermission.permission_id, Permission.permission_code == permission_code).first()

        if permission is None:
            raise HTTPException(
                status_code=403, detail="You don't have permission to perfom this action!"
            )
        return permission


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv(
            "SECRET_KEY", ""), algorithms=os.getenv("ALGORITHM", ""))
        username: str = str(payload.get("sub"))
        user_id: int = int(payload.get("id", 0))
        if username is None or user_id is None:
            raise credentials_exception
        return {'username': username, "user_id": user_id}
    except JWTError as error:
        raise credentials_exception from error

import os
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from typing import List
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from models import Users, UserRole
from schemas.ecsa_conf import TokenSchema, UserSchema, ResertPasswordSchema
from database import get_db
import utils
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_schema: UserSchema, db: Session = Depends(get_db)):
    existing_email = db.query(Users).filter(Users.email == user_schema.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_phone = db.query(Users).filter(Users.phone == user_schema.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already exists")

    password = utils.generate_random_password()

    create_user_model = Users(
        firstname=user_schema.firstname,
        lastname=user_schema.lastname,
        phone=user_schema.phone,
        email=user_schema.email,
        hashed_password=bcrypt.hash(password),
        verified=1,
    )

    db.add(create_user_model)
    db.commit()
    utils.new_account_email(user_schema.email, user_schema.firstname, password)
    return user_schema


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )

    token = create_access_token(user.email, user.id, timedelta(minutes=20))

    user_response = get_user_response(user)

    permissions = get_user_permissions(db, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response,
        "permissions": permissions,
    }


def authenticate_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = str(payload.get("sub"))
        user_id: int = int(payload.get("id", 0))
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


def get_user_response(user: Users) -> dict:
    return {
        "id": user.id,
        "phone": user.phone,
        "email": user.email,
        "verified": user.verified,
        "updated_at": user.updated_at,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "created_at": user.created_at,
    }


def get_user_permissions(db: Session, user_id: int) -> List[str]:
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    permissions = [
        rp.permission.permission_code
        for user_role in user_roles
        for rp in user_role.role.role_permission
    ]
    return permissions


@router.post("/reset_password/", status_code=status.HTTP_201_CREATED)
async def reset_password(
    reset_password_schema: ResertPasswordSchema, db: Session = Depends(get_db)
):
    user_email_model = (
        db.query(Users).filter(Users.email == reset_password_schema.username).first()
    )

    password = utils.generate_random_password()

    user_email_model.hashed_password = bcrypt.hash(password)

    db.commit()
    db.refresh(user_email_model)

    utils.password_change_email(
        user_email_model.email, user_email_model.firstname, password
    )
    raise HTTPException(status_code=200, detail="Password updated successfully")

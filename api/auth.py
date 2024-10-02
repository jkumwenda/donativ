from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = "1973chewi834929dnsdkdsifk437476399vnlkvdhsdfgsdf734943fmlmdsklsdkl"
ALGORITHM = "HS256"

bycrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


class CreateUserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    contact: str
    department: int
    role: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    hashed_password = bycrypt_context.hash(create_user_request.password)
    create_user_model = User(
        firstname=create_user_request.firstname,
        lastname=create_user_request.lastname,
        email=create_user_request.email,
        contact=create_user_request.contact,
        department=create_user_request.department,
        role=create_user_request.role,
        password=hashed_password,
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)


@router.post("/token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token_expires_delta = timedelta(minutes=20)
    token = create_access_token(
        user.firstname,
        user.lastname,
        user.email,
        user.department,
        user.id,
        token_expires_delta,
    )
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not bycrypt_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return user


def create_access_token(
    firstname: str,
    lastname: str,
    email: str,
    department: int,
    user_id: int,
    expires_delta: timedelta,
):
    to_encode = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "department": department,
        "user_id": user_id,
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("name")
        user_id: int = payload.get("user_id")
        if name is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"name": name, "user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

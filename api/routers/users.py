

from schemas.donativ import UserSchema, UserRoleSchema
from passlib.hash import bcrypt
import utils.mailer_util as mailer_util
import math
from sqlalchemy import or_
from starlette import status
from typing import Annotated
from core.database import get_db
from sqlalchemy.orm import Session
from dependencies.auth_dependency import Auth
from models.models import User, UserRole
from dependencies.dependency import Dependency
from dependencies.auth_dependency import get_current_user
from schemas.donativ import RoleSchema, RolePermissionSchema
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    status, Request
)


router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_dependency(db: Session = Depends(get_db)) -> Dependency:
    return Dependency(db)


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(
            status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_users(
    request: Request,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_USER", current_user["user_id"])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'VIEW_USERS',
        current_user['username'],
        client_ip,
        "Get all users"
    )

    search_filter = or_(
        User.firstname.ilike(f"%{search}%"),
        User.lastname.ilike(f"%{search}%"),
        User.email.ilike(f"%{search}%"),
    )

    users_query = db.query(User).filter(search_filter)

    total_count = users_query.count()
    users = users_query.offset(
        (skip - 1) * limit).limit(limit).all()

    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": users}


@router.post("/")
async def add_user(
    user_schema: UserSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_USER", user["id"], db)

    existing_email = db.query(Users).filter(
        Users.email == user_schema.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_phone = db.query(Users).filter(
        Users.phone == user_schema.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=400, detail="Phone number already exists")

    password = mailer_util.generate_random_password()

    hashed_password = bcrypt.hash(password)
    create_user_model = Users(
        firstname=user_schema.firstname,
        lastname=user_schema.lastname,
        phone=user_schema.phone,
        email=user_schema.email,
        hashed_password=hashed_password,
        verified=1,
    )

    db.add(create_user_model)
    db.commit()
    mailer_util.new_account_email(
        user_schema.email, user_schema.firstname, password)
    return user_schema

# @router.get("/{user_id}")
# async def get_user(
#     user_id: int,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("VIEW_USER", user["id"], db)
#     model = Users
#     user = get_object(user_id, db, model)

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     return {
#         "user": {
#             "id": user.id,
#             "firstname": user.firstname,
#             "lastname": user.lastname,
#             "phone": user.phone,
#             "email": user.email,
#             "participant": user.participant,
#         },
#         "roles": [
#             {
#                 "id": role.id,
#                 "role_id": role.role.id,
#                 "role": role.role.role,
#             }
#             for role in user.user_role
#         ],
#         "events": [
#             {
#                 "id": event.id,
#                 # "file_name": signature.file_name,
#                 # "file_location": signature.file_location,
#             }
#             for event in user.user_event
#         ],
#     }


# @router.put("/{user_id}")
# async def update_user(
#     user_id: int,
#     user: user_dependency,
#     user_schema: UserSchema,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("UPDATE_USER", user["id"], db)
#     user_model = get_object(user_id, db, Users)

#     user_model.firstname = user_schema.firstname
#     user_model.lastname = user_schema.lastname
#     user_model.phone = user_schema.phone
#     user_model.email = user_schema.email

#     db.commit()
#     db.refresh(user_model)
#     return user_schema


# @router.delete("/{user_id}")
# async def delete_user(
#     user_id: int,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("DELETE_USER", user["id"], db)
#     get_object(user_id, db, Users)
#     db.query(Users).filter(Users.id == user_id).delete()
#     db.commit()
#     raise HTTPException(
#         status_code=status.HTTP_200_OK, detail="Users Successfully deleted"
#     )


# @router.put("/password/{user_id}")
# async def update_password(
#     user_id: int,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("UPDATE_USER", user["id"], db)
#     user = get_object(user_id, db, Users)
#     password = mailer_util.generate_random_password()

#     db.query(Users).filter(Users.id == user_id).update(
#         {"hashed_password": mailer_util.hash_password(password)}
#     )
#     db.commit()
#     # Send a confirmation email (you can customize this part)
#     mailer_util.password_change_email(user.email, user.firstname, password)
#     raise HTTPException(
#         status_code=200, detail="Password updated successfully")


# @router.put("/reset_password/{user_id}")
# async def reset_password(
#     user_id: int,
#     user: user_dependency,
#     password_schema: PasswordSchema,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("UPDATE_USER", user["id"], db)
#     user = get_object(user_id, db, Users)
#     password = password_schema.password

#     db.query(Users).filter(Users.id == user_id).update(
#         {"hashed_password": mailer_util.hash_password(password)}
#     )
#     db.commit()
#     # Send a confirmation email (you can customize this part)
#     mailer_util.password_change_email(user.email, user.firstname, password)
#     raise HTTPException(
#         status_code=200, detail="Password rest was successfull")


# @router.post("/roles/")
# async def add_user_role(
#     user_role_schema: UserRoleSchema,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("ADD_USER", user["id"], db)
#     user_role_model = UserRole(
#         user_id=user_role_schema.user_id, role_id=user_role_schema.role_id
#     )

#     db.add(user_role_model)
#     db.commit()
#     db.refresh(user_role_model)
#     return user_role_model


# @router.put("/roles/{user_role_id}")
# async def update_user_role(
#     user_role_id: int,
#     user_role_schema: UserRoleSchema,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("UPDATE_USER", user["id"], db)
#     user_role_model = db.query(UserRole).filter(
#         UserRole.id == user_role_id).first()
#     user_role_model.user_id = (user_role_schema.user_id,)
#     user_role_model.role_id = user_role_schema.role_id
#     db.add(user_role_model)
#     db.commit()
#     db.refresh(user_role_model)
#     return user_role_model


# @router.delete("/roles/{user_role_id}")
# async def delete_user_role(
#     user_role_id: int,
#     user: user_dependency,
#     db: Session = Depends(get_db),
# ):
#     security.secureAccess("DELETE_USER", user["id"], db)

#     db.query(UserRole).filter(UserRole.id == user_role_id).delete()
#     db.commit()
#     raise HTTPException(
#         status_code=200, detail="Users role successfully deleted")

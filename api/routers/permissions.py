from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from models import Permission
from schemas.ecsa_conf import PermissionSchema
from sqlalchemy.orm import Session
from database import get_db
from .auth import get_current_user
from typing import Annotated
from sqlalchemy import or_
import math

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_permissions(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    # security.secureAccess("READ_BRANCH", user_id, db)

    offset = (skip - 1) * limit
    query = (
        db.query(Permission)
        .filter(or_(Permission.permission.ilike(f"%{search}%")))
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(Permission)
        .filter(or_(Permission.permission.ilike(f"%{search}%")))
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def add_permission(
    permission_schema: PermissionSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    # security.secureAccess("WRITE_BRANCH", user_id, db)
    create_permission_model = Permission(
        permission=permission_schema.permission,
        description=permission_schema.description,
    )

    db.add(create_permission_model)
    db.commit()
    return permission_schema


@router.get("/{permission_id}")
async def get_permission(
    permission_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    # security.secureAccess("READ_BRANCH", user_id, db)
    return get_object(permission_id, db, Permission)


@router.put("/{permission_id}")
async def update_permission(
    permission_id: int,
    user: user_dependency,
    permission_schema: PermissionSchema,
    db: Session = Depends(get_db),
):
    # security.secureAccess("UPDATE_BRANCH", user_id, db)
    permission_model = get_object(permission_id, db, Permission)

    permission_model.permission = permission_schema.permission
    permission_model.description = permission_schema.description

    db.commit()
    db.refresh(permission_model)
    return permission_schema


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
):
    # security.secureAccess("DELETE_BRANCH", user_id, db)
    get_object(permission_id, db, Permission)
    db.query(Permission).filter(Permission.id == permission_id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="Permission Successfully deleted"
    )

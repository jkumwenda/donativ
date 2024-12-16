import math
from sqlalchemy import or_
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import Permission
from schemas.donativ import PermissionSchema
from dependencies.auth_dependency import Auth
from dependencies.dependency import Dependency
from dependencies.auth_dependency import get_current_user
from fastapi import APIRouter, HTTPException, Depends, Query, Request

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
async def get_permissions(
    request: Request,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_PERMISSION", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'VIEW_PERMISSIONS',
        current_user['username'],
        client_ip,
        "Get all permissions"
    )

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
    request: Request,
    permission_schema: PermissionSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADD_PERMISSION", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ADD_PERMISSION',
        current_user['username'],
        client_ip,
        permission_schema.permission_code
    )

    create_permission_model = Permission(
        system_code=permission_schema.system_code,
        permission=permission_schema.permission,
        permission_code=permission_schema.permission_code,
    )

    db.add(create_permission_model)
    db.commit()
    return permission_schema


@router.get("/{permission_id}")
async def get_permission(
    request: Request,
    permission_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_PERMISSION", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'VIEW_PERMISSION',
        current_user['username'],
        client_ip,
        f"View permission id {permission_id}"
    )
    return get_object(permission_id, db, Permission)


@router.put("/{permission_id}")
async def update_permission(
    request: Request,
    permission_id: int,
    current_user: user_dependency,
    permission_schema: PermissionSchema,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("UPDATE_PERMISSION", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'UPDATE_PERMISION',
        current_user['username'],
        client_ip,
        f"Update permission id {permission_id} permission code {permission_schema.permission_code}"
    )

    permission_model = get_object(permission_id, db, Permission)

    permission_model.permission = permission_schema.permission
    permission_model.permission_code = permission_schema.permission_code

    db.commit()
    db.refresh(permission_model)
    return permission_schema


@router.delete("/{permission_id}")
async def delete_permission(
    request: Request,
    permission_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("DELETE_PERMISSION", current_user['user_id'])
    permission = get_object(permission_id, db, Permission)

    try:
        db.delete(permission)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission") from error

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'DELETE_PERMISION',
        current_user['username'],
        client_ip,
        f"Update permission id {permission_id}, permission {permission.permission_code} "
    )
    return {"detail": "Permission successfully deleted"}

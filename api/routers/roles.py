import math
from sqlalchemy import or_
from starlette import status
from typing import Annotated
from core.database import get_db
from sqlalchemy.orm import Session
from dependencies.auth_dependency import Auth
from models.models import Role, RolePermission
from dependencies.dependency import Dependency
from dependencies.auth_dependency import get_current_user
from schemas.donativ import RoleSchema, RolePermissionSchema
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
async def get_roles(
    request: Request,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_ROLE", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'VIEW_ROLES',
        current_user['username'],
        client_ip,
        "Get all roles"
    )

    search_filter = or_(
        Role.role.ilike(f"%{search}%"),
        Role.description.ilike(f"%{search}%")
    )

    roles_query = db.query(Role).filter(search_filter)

    total_count = roles_query.count()
    roles = roles_query.offset(
        (skip - 1) * limit).limit(limit).all()

    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": roles}


@router.post("/")
async def add_role(
    request: Request,
    role_schema: RoleSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADD_ROLE", current_user["user_id"])

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ADD_ROLE',
        current_user['username'],
        client_ip,
        role_schema.role
    )

    create_role_model = Role(
        role=role_schema.role,
        description=role_schema.description,
    )

    db.add(create_role_model)
    db.commit()
    return role_schema


@router.get("/{role_id}")
async def get_role(
    request: Request,
    role_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_ROLE", current_user["user_id"])
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user['user_id'],
        'VIEW_ROLE',
        current_user['username'],
        client_ip,
        f"View role id {role_id} and associated permissions"
    )

    if role := get_object(role_id, db, Role):
        return {
            "role": {
                "id": role.id,
                "role": role.role,
                "description": role.description,
            },
            "permissions": [
                {
                    "id": permission.id,
                    "permission_id": permission.permission.id,
                    "permission": permission.permission.permission,
                    "permission_code": permission.permission.permission_code,
                }
                for permission in role.role_permission
            ],
        }
    else:
        raise HTTPException(status_code=404, detail="Role not found")


@router.put("/{role_id}")
async def update_role(
    request: Request,
    role_id: int,
    current_user: user_dependency,
    role_schema: RoleSchema,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access("UPDATE_ROLE", current_user["user_id"])

    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user['user_id'],
        'UPDATE_ROLE',
        current_user['username'],
        client_ip,
        f"Update role id {role_id}"
    )

    role_model = get_object(role_id, db, Role)

    role_model.role = role_schema.role
    role_model.description = role_schema.description

    db.commit()
    db.refresh(role_model)
    return role_schema


@router.delete("/{role_id}")
async def delete_role(
    request: Request,
    role_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access("DELETE_ROLE", current_user["user_id"])

    client_ip = dependency.request_ip(request)
    role = get_object(role_id, db, Role)

    try:
        db.delete(role)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role") from error

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'DELETE_ROLE',
        current_user['username'],
        client_ip,
        f"Delete role id {role_id} role {role.role}"
    )
    return {"detail": "Role Successfully deleted"}


@router.post("/permissions/")
async def add_role_permission(
    request: Request,
    role_permission_schema: RolePermissionSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access("ADD_ROLE", current_user["user_id"])

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ADD_ROLE_PERMISSION',
        current_user['username'],
        client_ip,
        f"Role id {role_permission_schema.role_id} Permission id {role_permission_schema.permission_id}"
    )

    role_permission_model = RolePermission(
        permission_id=role_permission_schema.permission_id,
        role_id=role_permission_schema.role_id,
    )
    db.add(role_permission_model)
    db.commit()
    db.refresh(role_permission_model)
    return role_permission_model


@router.put("/permissions/{role_permission_id}")
async def update_role_permission(
    request: Request,
    role_permission_id: int,
    role_permission_schema: RolePermissionSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access("UPDATE_ROLE", current_user["id"])

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'UPDATE_ROLE_PERMISSION',
        current_user['username'],
        client_ip,
        f"Role id {role_permission_schema.role_id} Permission id {role_permission_schema.permission_id}"
    )

    role_permission_model = (
        db.query(RolePermission).filter(
            RolePermission.id == role_permission_id).first()
    )
    role_permission_model.permission_id = (
        role_permission_schema.permission_id,)
    role_permission_model.role_id = (role_permission_schema.role_id,)

    db.add(role_permission_model)
    db.commit()
    db.refresh(role_permission_model)
    return role_permission_model


@router.delete("/permissions/{role_permission_id}")
async def delete_role_permission(
    request: Request,
    role_permission_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access("DELETE_PERMISSION", current_user["user_id"])
    role_permission = get_object(
        role_permission_id, db, RolePermission)
    try:
        db.delete(role_permission)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role permission") from error

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'DELETE_ROLE_PERMISSION',
        current_user['username'],
        client_ip,
        f"Delete role permission id {role_permission_id}"
    )
    return {"detail": "Role permission successfully deleted"}

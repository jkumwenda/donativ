from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from models import Role, RolePermission
from schemas.ecsa_conf import RoleSchema, RolePermissionSchema
from sqlalchemy.orm import Session
from database import get_db
from .auth import get_current_user
from typing import Annotated
from sqlalchemy import or_
import math
from dependencies import Security

router = APIRouter()

security = Security()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_roles(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    security.secureAccess("VIEW_ROLE", user["id"], db)
    offset = (skip - 1) * limit
    query = (
        db.query(Role)
        .filter(
            or_(Role.role.ilike(f"%{search}%"), Role.description.ilike(f"%{search}%"))
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(Role)
        .filter(
            or_(Role.role.ilike(f"%{search}%"), Role.description.ilike(f"%{search}%"))
        )
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def add_role(
    role_schema: RoleSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_ROLE", user["id"], db)
    create_role_model = Role(
        role=role_schema.role,
        description=role_schema.description,
    )

    db.add(create_role_model)
    db.commit()
    return role_schema


@router.get("/{role_id}")
async def get_role(
    role_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("VIEW_ROLE", user["id"], db)
    role = get_object(role_id, db, Role)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

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


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    user: user_dependency,
    role_schema: RoleSchema,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_ROLE", user["id"], db)
    role_model = get_object(role_id, db, Role)

    role_model.role = role_schema.role
    role_model.description = role_schema.description

    db.commit()
    db.refresh(role_model)
    return role_schema


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_ROLE", user["id"], db)
    get_object(role_id, db, Role)
    db.query(Role).filter(Role.id == role_id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="Role Successfully deleted"
    )


@router.post("/permissions/")
async def add_role_permission(
    role_permission_schema: RolePermissionSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_ROLE", user["id"], db)
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
    role_permission_id: int,
    role_permission_schema: RolePermissionSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_ROLE", user["id"], db)
    role_permission_model = (
        db.query(RolePermission).filter(RolePermission.id == role_permission_id).first()
    )
    role_permission_model.permission_id = (role_permission_schema.permission_id,)
    role_permission_model.role_id = (role_permission_schema.role_id,)

    db.add(role_permission_model)
    db.commit()
    db.refresh(role_permission_model)
    return role_permission_model


@router.delete("/permissions/{role_permission_id}")
async def delete_role_permission(
    role_permission_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_ROLE", user["id"], db)
    db.query(RolePermission).filter(RolePermission.id == role_permission_id).delete()
    db.commit()
    raise HTTPException(status_code=200, detail="Role permission successfully deleted")

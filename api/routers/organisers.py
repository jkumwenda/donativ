from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from models import Organiser
from schemas.ecsa_conf import OrganiserSchema
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
async def get_organisers(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    security.secureAccess("VIEW_ORGANISER", user["id"], db)

    offset = (skip - 1) * limit
    query = (
        db.query(Organiser)
        .filter(
            or_(
                Organiser.organiser.ilike(f"%{search}%"),
                Organiser.description.ilike(f"%{search}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(Organiser)
        .filter(
            or_(
                Organiser.organiser.ilike(f"%{search}%"),
                Organiser.description.ilike(f"%{search}%"),
            )
        )
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def add_organiser(
    organiser_schema: OrganiserSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_ORGANISER", user["id"], db)
    create_organiser_model = Organiser(
        organiser=organiser_schema.organiser,
        description=organiser_schema.description,
    )

    db.add(create_organiser_model)
    db.commit()
    return organiser_schema


@router.get("/{organiser_id}")
async def get_organiser(
    organiser_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("VIEW_ORGANISER", user["id"], db)
    organiser = get_object(organiser_id, db, Organiser)
    if not organiser:
        raise HTTPException(status_code=404, detail="Organiser not found")

    return {
        "organiser": {
            "id": organiser.id,
            "organiser": organiser.organiser,
            "description": organiser.description,
        },
    }


@router.put("/{organiser_id}")
async def update_organiser(
    organiser_id: int,
    user: user_dependency,
    organiser_schema: OrganiserSchema,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_ORGANISER", user["id"], db)
    organiser_model = get_object(organiser_id, db, Organiser)

    organiser_model.organiser = organiser_schema.organiser
    organiser_model.description = organiser_schema.description

    db.commit()
    db.refresh(organiser_model)
    return organiser_schema


@router.delete("/{organiser_id}")
async def delete_organiser(
    organiser_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_ORGANISER", user["id"], db)
    get_object(organiser_id, db, Organiser)
    db.query(Organiser).filter(Organiser.id == organiser_id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Organiser successfully deleted",
    )

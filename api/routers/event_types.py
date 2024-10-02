from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from models import EventType
from schemas.ecsa_conf import EventTypeSchema
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
async def get_event_types(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    security.secureAccess("VIEW_EVENT_TYPE", user["id"], db)

    offset = (skip - 1) * limit
    query = (
        db.query(EventType)
        .filter(
            or_(
                EventType.event_type.ilike(f"%{search}%"),
                EventType.description.ilike(f"%{search}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(EventType)
        .filter(
            or_(
                EventType.event_type.ilike(f"%{search}%"),
                EventType.description.ilike(f"%{search}%"),
            )
        )
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def add_event_type(
    event_type_schema: EventTypeSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_EVENT_TYPE", user["id"], db)
    create_event_type_model = EventType(
        event_type=event_type_schema.event_type,
        description=event_type_schema.description,
    )

    db.add(create_event_type_model)
    db.commit()
    return event_type_schema


@router.get("/{event_type_id}")
async def get_event_type(
    event_type_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("VIEW_EVENT_TYPE", user["id"], db)
    event_type = get_object(event_type_id, db, EventType)
    if not event_type:
        raise HTTPException(status_code=404, detail="EventType not found")

    return {
        "event_type": {
            "id": event_type.id,
            "event_type": event_type.event_type,
            "description": event_type.description,
        },
    }


@router.put("/{event_type_id}")
async def update_event_type(
    event_type_id: int,
    user: user_dependency,
    event_type_schema: EventTypeSchema,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_EVENT_TYPE", user["id"], db)
    event_type_model = get_object(event_type_id, db, EventType)

    event_type_model.event_type = event_type_schema.event_type
    event_type_model.description = event_type_schema.description

    db.commit()
    db.refresh(event_type_model)
    return event_type_schema


@router.delete("/{event_type_id}")
async def delete_event_type(
    event_type_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_EVENT_TYPE", user["id"], db)
    get_object(event_type_id, db, EventType)
    db.query(EventType).filter(EventType.id == event_type_id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="EventType successfully deleted",
    )

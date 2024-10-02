from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile
from models import Event, Country, EventType, Organiser, Users, Participant
from sqlalchemy.orm import Session, joinedload
from database import get_db
from .auth import get_current_user
from typing import Annotated
from sqlalchemy import or_
import math
from dependencies import Security
from datetime import datetime
from fastapi.responses import JSONResponse
import shutil
import uuid
import os


router = APIRouter()
security = Security()
user_dependency = Annotated[dict, Depends(get_current_user)]

UPLOAD_DIR = "uploads/profile_pictures"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.get("/")
async def dashboard(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    security.secureAccess("VIEW_DASHBOARD", user["id"], db)
    current_time = datetime.now()

    user = db.query(Users).filter(Users.id == user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    participant = db.query(Participant).filter(Participant.user_id == user.id).first()

    user_details = {
        "user": {
            "id": user.id,
            "participant_id": participant.id,
            "title": participant.title,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "phone": user.phone,
            "email": user.email,
            "institution": participant.institution,
            "country": participant.country.country,
            "country_id": participant.country.id,
            "picture": participant.picture,
        },
        "user_events": [
            {
                "user_event_id": user_event.id,
                "participant_category": user_event.participant_category,
                "confirm_attendance": user_event.confirm_attendance,
                "event_badge": user_event.event_badge,
                "event_payment": user_event.event_payment,
                "event_id": user_event.event_id,
                "event": user_event.event.event,
                "event_type": user_event.event.event_type.event_type,
                "country_id": user_event.event.country.id,
                "country": user_event.event.country.country,
                "organiser_id": user_event.event.organiser.id,
                "organiser": user_event.event.organiser.organiser,
                "location": user_event.event.location,
                "description": user_event.event.description,
                "capacity": user_event.event.capacity,
                "start_date": user_event.event.start_date,
                "end_date": user_event.event.end_date,
                "registration_start_date": user_event.event.registration_start_date,
                "registration_end_date": user_event.event.registration_end_date,
            }
            for user_event in user.user_event
        ],
    }

    current_events = (
        db.query(Event)
        .join(Country, Event.country_id == Country.id)
        .join(EventType, Event.event_type_id == EventType.id)
        .join(Organiser, Event.organiser_id == Organiser.id)
        .filter(or_(Event.end_date > current_time))
        .options(
            joinedload(Event.country),
            joinedload(Event.organiser),
            joinedload(Event.event_type),
        )
        .all()
    )
    return {"user_details": user_details, "current_events": current_events}


@router.post("/upload_profile/")
async def create_upload_file(
    user: user_dependency,
    profilePicture: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Generate a unique filename
    extension = os.path.splitext(profilePicture.filename)[1]  # Get the file extension
    new_filename = (
        f"{uuid.uuid4()}{extension}"  # Generate a new filename with the same extension
    )

    # Save the file with the new filename
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profilePicture.file, buffer)

    participant_model = (
        db.query(Participant).filter(Participant.user_id == user["id"]).first()
    )

    participant_model.picture = file_path

    db.commit()
    db.refresh(participant_model)

    return JSONResponse({"filename": file_path})

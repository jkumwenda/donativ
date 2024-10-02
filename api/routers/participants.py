from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from models import Country, Participant, Users, UserRole, UserEvent
from schemas.ecsa_conf import ParticipantSchema
from sqlalchemy.orm import Session, joinedload
from database import get_db
from .auth import get_current_user
from typing import Annotated
from sqlalchemy import or_
import math
from dependencies import Security
import utils
from passlib.hash import bcrypt

router = APIRouter()

security = Security()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_participants(
    user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    security.secureAccess("VIEW_PARTICIPANT", user["id"], db)

    offset = (skip - 1) * limit
    query = (
        db.query(Participant)
        .join(Country, Participant.country_id == Country.id)
        .join(Users, Participant.user_id == Users.id)
        .filter(
            or_(
                Participant.title.ilike(f"%{search}%"),
                Users.firstname.ilike(f"%{search}%"),
                Users.lastname.ilike(f"%{search}%"),
                Country.country.ilike(f"%{search}%"),
            )
        )
        .options(
            joinedload(Participant.country),
            joinedload(Participant.users),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(Participant)
        .join(Country, Participant.country_id == Country.id)
        .join(Users, Participant.user_id == Users.id)
        .filter(
            or_(
                Participant.title.ilike(f"%{search}%"),
                Users.firstname.ilike(f"%{search}%"),
                Users.lastname.ilike(f"%{search}%"),
                Country.country.ilike(f"%{search}%"),
            )
        )
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def register_participant(
    participant_schema: ParticipantSchema,
    db: Session = Depends(get_db),
):

    existing_email = (
        db.query(Users).filter(Users.email == participant_schema.email).first()
    )
    if existing_email:
        raise HTTPException(
            status_code=400, detail="Email already exists, please login"
        )

    existing_phone = (
        db.query(Users).filter(Users.phone == participant_schema.phone).first()
    )
    if existing_phone:
        raise HTTPException(
            status_code=400, detail="Phone number already exists, login or reset"
        )

    password = utils.generate_random_password()

    create_user_model = Users(
        firstname=participant_schema.firstname,
        lastname=participant_schema.lastname,
        phone=participant_schema.phone,
        email=participant_schema.email,
        hashed_password=bcrypt.hash(password),
        verified=1,
    )
    db.add(create_user_model)
    db.commit()

    create_participant_model = Participant(
        user_id=create_user_model.id,
        country_id=participant_schema.country_id,
        title=participant_schema.title,
        institution=participant_schema.institution,
    )

    db.add(create_participant_model)
    db.commit()

    create_user_role_model = UserRole(
        user_id=create_user_model.id,
        role_id=2,
    )

    db.add(create_user_role_model)
    db.commit()

    utils.new_account_email(
        participant_schema.email, participant_schema.firstname, password
    )
    return participant_schema


@router.get("/{participant_id}")
async def get_participant(
    participant_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("VIEW_PARTICIPANT", user["id"], db)

    # participant = get_object(participant_id, db, Participant)
    participant = (
        db.query(Participant).filter(Participant.user_id == participant_id).first()
    )

    user = db.query(Users).filter(Users.id == participant.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User record not found")

    if not participant:
        raise HTTPException(status_code=404, detail="Participant record not found")

    return {
        "participant": {
            "id": user.id,
            "participant_id": participant.id if participant.id else 0,
            "title": participant.title,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "phone": user.phone,
            "email": user.email,
            "institution": participant.institution,
            "country": participant.country.country,
            "country_id": participant.country.id,
        },
        "events": [
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


@router.put("/{participant_id}")
async def update_participant(
    participant_id: int,
    user: user_dependency,
    participant_schema: ParticipantSchema,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_PARTICIPANT", user["id"], db)

    participant_model = (
        db.query(Participant).filter(Participant.user_id == participant_id).first()
    )
    user_id = participant_model.user_id
    user_model = get_object(user_id, db, Users)

    user_model.email = participant_schema.email
    user_model.firstname = participant_schema.firstname
    user_model.lastname = participant_schema.lastname
    user_model.phone = participant_schema.phone

    participant_model.title = participant_schema.title
    participant_model.institution = participant_schema.institution
    participant_model.country_id = participant_schema.country_id

    db.commit()
    db.refresh(user_model)
    db.refresh(participant_model)
    return participant_schema


@router.delete("/{participant_id}")
async def delete_participant(
    participant_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_PARTICIPANT", user["id"], db)

    participant = get_object(participant_id, db, Participant)

    db.query(Participant).filter(Participant.id == participant_id).delete()
    db.commit()

    # user_role = (
    #     db.query(UserRole).filter(UserRole.user_id == participant.user_id).first()
    # )

    # db.query(UserRole).filter(UserRole.id == user_role.id).delete()
    # db.commit()

    db.query(Users).filter(Users.id == participant.user_id).delete()
    db.commit()

    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="Participant successfully deleted"
    )


@router.put("/paid/{participant_id}")
async def update_participant(
    participant_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_PARTICIPANT", user["id"], db)

    participant_model = get_object(participant_id, db, Participant)

    user_event_model = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == participant_model.user_id)
        .first()
    )

    user_event_model.event_payment = 1

    db.commit()
    db.refresh(participant_model)
    return {"Paid": "Paid succesfully"}

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    File,
    Form,
    UploadFile,
    Response,
)
from starlette import status
from models import (
    Event,
    Country,
    EventType,
    Organiser,
    UserEvent,
    Participant,
    Users,
    UserRole,
    EventResourceFile,
    EventLink,
    UserEventAttendance,
)
from schemas.ecsa_conf import (
    EventSchema,
    EventRegistrationSchema,
    PaymentSchema,
    OnlinePaymentSchema,
    UserEventSchema,
    EventLinkSchema,
    EventPaymentSchema,
    EventAttendanceSchema,
)
from sqlalchemy.orm import Session, joinedload
from database import get_db
from .auth import get_current_user
from typing import Annotated
from sqlalchemy import or_, func
import math
from dependencies import Security
from datetime import datetime
from fastapi.responses import JSONResponse
from reportlab.pdfgen import canvas
import pandas as pd
from io import BytesIO, StringIO
import math
import utils
from passlib.hash import bcrypt
import os
import random
import string
from datetime import datetime


router = APIRouter()
security = Security()
user_dependency = Annotated[dict, Depends(get_current_user)]


UPLOAD_DIR = "uploads/files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_events(
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    offset = (skip - 1) * limit
    query = (
        db.query(Event)
        .join(Country, Event.country_id == Country.id)
        .join(EventType, Event.event_type_id == EventType.id)
        .join(Organiser, Event.organiser_id == Organiser.id)
        .filter(or_(Event.event.ilike(f"%{search}%")))
        .options(
            joinedload(Event.country),
            joinedload(Event.organiser),
            joinedload(Event.event_type),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = db.query(Event).filter(or_(Event.event.ilike(f"%{search}%"))).count()
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/")
async def add_event(
    event_schema: EventSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_EVENT", user["id"], db)
    create_event_model = Event(
        event_type_id=event_schema.event_type_id,
        country_id=event_schema.country_id,
        organiser_id=event_schema.organiser_id,
        event=event_schema.event,
        location=event_schema.location,
        capacity=event_schema.capacity,
        description=event_schema.description,
        start_date=event_schema.start_date,
        end_date=event_schema.end_date,
        registration_start_date=event_schema.registration_start_date,
        registration_end_date=event_schema.registration_end_date,
    )
    db.add(create_event_model)
    db.commit()
    return event_schema


@router.get("/{event_id}")
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    event_data = (
        db.query(
            Event.id,
            EventType.event_type,
            Event.event_type_id,
            Country.country,
            Event.country_id,
            Organiser.organiser,
            Event.organiser_id,
            Event.event,
            Event.location,
            Event.description,
            Event.capacity,
            Event.start_date,
            Event.end_date,
            Event.registration_start_date,
            Event.registration_end_date,
        )
        .join(EventType, Event.event_type_id == EventType.id)
        .join(Country, Event.country_id == Country.id)
        .join(Organiser, Event.organiser_id == Organiser.id)
        .filter(Event.id == event_id)
        .first()
    )
    event = {
        "id": event_data.id,
        "event_type": event_data.event_type,
        "event_type_id": event_data.event_type_id,
        "country": event_data.country,
        "country_id": event_data.country_id,
        "organiser": event_data.organiser,
        "organiser_id": event_data.organiser_id,
        "event": event_data.event,
        "location": event_data.location,
        "description": event_data.description,
        "capacity": event_data.capacity,
        "start_date": event_data.start_date,
        "end_date": event_data.end_date,
        "registration_start_date": event_data.registration_start_date,
        "registration_end_date": event_data.registration_end_date,
    }

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    offset = (skip - 1) * limit

    # Specify the columns to retrieve
    query = (
        db.query(
            Users.id,
            Participant.title,
            Users.firstname,
            Users.lastname,
            Users.email,
            Users.phone,
            Participant.institution,
            Country.country,
            Participant.picture,
            UserEvent.participant_category,
            UserEvent.confirm_attendance,
            UserEvent.event_badge,
            UserEvent.event_payment,
        )
        .join(Participant, Participant.user_id == Users.id)
        .join(UserEvent, UserEvent.user_id == Users.id)
        .join(Country, Country.id == Participant.country_id)
        .filter(
            UserEvent.event_id == event_id,
            or_(
                Users.firstname.ilike(f"%{search}%"),
                Users.lastname.ilike(f"%{search}%"),
                Users.email.ilike(f"%{search}%"),
            ),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    resource_files = (
        db.query(EventResourceFile)
        .filter(
            EventResourceFile.event_id == event_id,
        )
        .all()
    )
    links = (
        db.query(EventLink)
        .filter(
            EventLink.event_id == event_id,
        )
        .all()
    )
    attendance_query = (
        db.query(
            Users.id,
            Participant.title,
            Users.firstname,
            Users.lastname,
            Users.email,
            Event.event,
            Event.start_date,
            Event.end_date,
            UserEventAttendance.date,
        )
        .join(Users, UserEventAttendance.user_id == Users.id)
        .join(Event, UserEventAttendance.event_id == Event.id)
        .join(Participant, Participant.user_id == Users.id)
        .filter(UserEventAttendance.event_id == event_id)
        .all()
    )
    attendance = [
        {
            "id": row[0],
            "title": row[1],
            "firstname": row[2],
            "lastname": row[3],
            "email": row[4],
            "event": row[5],
            "event_start_date": row[6].date(),
            "event_end_date": row[7].date(),
            "attendance_date": row[8].date(),
        }
        for row in attendance_query
    ]

    # Total count for pagination
    total_count = (
        db.query(Users)
        .join(UserEvent, UserEvent.user_id == Users.id)
        .filter(UserEvent.event_id == event_id)
        .count()
    )
    pages = math.ceil(total_count / limit)
    formatted_data = [
        {
            "id": user.id,
            "title": user.title,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "phone": user.phone,
            "institution": user.institution,
            "country": user.country,
            "picture": user.picture,
            "participant_category": user.participant_category,
            "confirm_attendance": user.confirm_attendance,
            "event_badge": user.event_badge,
            "event_payment": user.event_payment,
        }
        for user in query
    ]
    return {
        "pages": pages,
        "data": formatted_data,
        "attendance": attendance,
        "event": event,
        "resource_files": resource_files,
        "links": links,
    }


@router.put("/{event_id}")
async def update_event(
    event_id: int,
    user: user_dependency,
    event_schema: EventSchema,
    db: Session = Depends(get_db),
):
    security.secureAccess("UPDATE_EVENT", user["id"], db)
    event_model = get_object(event_id, db, Event)

    event_model.event_type_id = event_schema.event_type_id
    event_model.country_id = event_schema.country_id
    event_model.organiser_id = event_schema.organiser_id
    event_model.event = event_schema.event
    event_model.location = event_schema.location
    event_model.capacity = event_schema.capacity
    event_model.description = event_schema.description
    event_model.start_date = event_schema.start_date
    event_model.end_date = event_schema.end_date
    event_model.registration_start_date = event_schema.registration_start_date
    event_model.registration_end_date = event_schema.registration_end_date

    db.commit()
    db.refresh(event_model)
    return event_schema


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("DELETE_EVENT", user["id"], db)
    get_object(event_id, db, Event)
    db.query(Event).filter(Event.id == event_id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="Event successfully deleted"
    )


@router.get("/active/")
async def get_active_events(
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    offset = (skip - 1) * limit
    current_time = datetime.now()

    query = (
        db.query(Event)
        .join(Country, Event.country_id == Country.id)
        .join(EventType, Event.event_type_id == EventType.id)
        .join(Organiser, Event.organiser_id == Organiser.id)
        .filter(or_(Event.event.ilike(f"%{search}%")), Event.end_date >= current_time)
        .options(
            joinedload(Event.country),
            joinedload(Event.organiser),
            joinedload(Event.event_type),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = db.query(Event).filter(or_(Event.event.ilike(f"%{search}%"))).count()
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}


@router.post("/register/")
async def register(
    event_registration_schema: EventRegistrationSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):

    if user["id"] is None:
        raise HTTPException(
            status_code=404, detail="You need to login to register for an event"
        )

    create_user_event_model = UserEvent(
        event_id=event_registration_schema.event_id,
        participant_category=event_registration_schema.participant_category,
        user_id=user["id"],
    )
    db.add(create_user_event_model)
    db.commit()
    return event_registration_schema


@router.delete("/deregister/{event_id}")
async def deregister(
    event_id: int,
    user: user_dependency,
    db: Session = Depends(get_db),
):

    if user["id"] is None:
        raise HTTPException(
            status_code=404, detail="You can only deregister your registered events"
        )

    user_event = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == user["id"], UserEvent.event_id == event_id)
        .first()
    )

    db.query(UserEvent).filter(UserEvent.id == user_event.id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="User event successfully deleted"
    )


@router.post("/cancel_registration/")
async def cancel_registration(
    user_event_schema: UserEventSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    user_event = (
        db.query(UserEvent)
        .filter(
            UserEvent.user_id == user_event_schema.user_id,
            UserEvent.event_id == user_event_schema.event_id,
        )
        .first()
    )

    db.query(UserEvent).filter(UserEvent.id == user_event.id).delete()
    db.commit()
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail="User successfully deregistered"
    )


@router.post("/add_event_payment/")
async def add_event_payment(
    payment_schema: PaymentSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_EVENT", user["id"], db)

    data = (
        db.query(UserEvent)
        .filter(
            UserEvent.event_id == payment_schema.event_id,
            UserEvent.user_id == payment_schema.user_id,
        )
        .first()
    )
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event ID {payment_schema.event_id} and User ID {payment_schema.user_id} : Does not exist",
        )

    user_event_model = data
    user_event_model.confirm_attendance = True
    user_event_model.event_payment = True
    user_event_model.confirmation_code = payment_schema.transaction_code
    db.commit()
    db.refresh(user_event_model)
    return payment_schema


@router.post("/online_payment/")
async def online_payment(
    online_payment_schema: OnlinePaymentSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):

    if user["id"] is None:
        raise HTTPException(
            status_code=404, detail="You need to login to pay for an event"
        )
    return online_payment_schema


@router.post("/upload_participants/")
async def upload_participants(
    user: user_dependency,
    file: UploadFile = File(...),
    eventID: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        contents = await file.read()
        df = parse_file(contents, file.content_type)
        if df is None:
            return unsupported_file_response()

        if not validate_columns(df):
            return missing_columns_response()

        data = df.to_dict(orient="records")
        updated, added = process_records(data, eventID, db)

        return JSONResponse(
            content={
                "new": added,
                "updated": updated,
                "total_records": len(data),
                "data": data,
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )


def parse_file(contents: bytes, content_type: str):
    if content_type in [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]:
        return pd.read_excel(BytesIO(contents))
    elif content_type == "text/csv":
        return pd.read_csv(StringIO(contents.decode("utf-8")))
    else:
        return None


def unsupported_file_response():
    return JSONResponse(
        content={
            "status": "error",
            "message": "Unsupported file type. Please upload a CSV or Excel file.",
        },
        status_code=400,
    )


def validate_columns(df: pd.DataFrame) -> bool:
    expected_columns = {
        "EMAIL",
        "FIRSTNAME",
        "LASTNAME",
        "PHONE",
        "TITLE",
        "INSTITUTION",
        "COUNTRY",
        "PARTICIPANT_CATEGORY",
        "CONFIRM_ATTENDANCE",
        "EVENT_PAYMENT",
        "PAYMENT_CONFIRMATION_CODE",
    }
    return expected_columns.issubset(df.columns)


def missing_columns_response():
    return JSONResponse(
        content={
            "status": "error",
            "message": "File is missing one or more required columns.",
        },
        status_code=400,
    )


def process_records(data: list, eventID: int, db: Session):
    updated = 0
    added = 0

    for item in data:
        user_record = db.query(Users).filter(Users.email == item["EMAIL"]).first()
        country = db.query(Country).filter(Country.country == item["COUNTRY"]).first()

        if not country:
            return country_not_found_response(item["COUNTRY"])

        if user_record:
            updated += update_existing_user(user_record, item, country, eventID, db)
        else:
            added += add_new_user(item, country, eventID, db)

    return updated, added


def country_not_found_response(country: str):
    return JSONResponse(
        content={
            "status": "error",
            "message": f"Country '{country}' not found.",
        },
        status_code=400,
    )


def update_existing_user(user_record, item, country, eventID, db):
    user_record.email = item["EMAIL"]
    user_record.firstname = item["FIRSTNAME"]
    user_record.lastname = item["LASTNAME"]
    user_record.phone = item["PHONE"]
    db.commit()
    db.refresh(user_record)

    participant_model = (
        db.query(Participant).filter(Participant.user_id == user_record.id).first()
    )
    user_event_model = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == user_record.id, UserEvent.event_id == eventID)
        .first()
    )

    if not participant_model:
        participant_model = Participant(
            user_id=user_record.id,
            country_id=country.id,
            title=item["TITLE"],
            institution=item["INSTITUTION"],
        )
        db.add(participant_model)
        db.commit()
    else:
        participant_model.title = item["TITLE"]
        participant_model.institution = item["INSTITUTION"]
        participant_model.country_id = country.id
        db.commit()
        db.refresh(participant_model)

    if not user_event_model:
        user_event_model = UserEvent(
            user_id=user_record.id,
            event_id=eventID,
            participant_category=item["PARTICIPANT_CATEGORY"],
            confirm_attendance=item["CONFIRM_ATTENDANCE"],
            event_payment=item["EVENT_PAYMENT"],
            confirmation_code=item["PAYMENT_CONFIRMATION_CODE"],
        )
        db.add(user_event_model)
    else:
        user_event_model.participant_category = item["PARTICIPANT_CATEGORY"]
        user_event_model.confirm_attendance = int(item["CONFIRM_ATTENDANCE"])
        user_event_model.event_payment = int(item["EVENT_PAYMENT"])
        user_event_model.confirmation_code = item["PAYMENT_CONFIRMATION_CODE"]

    db.commit()
    db.refresh(user_event_model)
    return 1


def add_new_user(item, country, eventID, db):
    password = utils.generate_random_password()
    create_user_model = Users(
        firstname=item["FIRSTNAME"],
        lastname=item["LASTNAME"],
        phone=item["PHONE"],
        email=item["EMAIL"],
        hashed_password=bcrypt.hash(password),
        verified=1,
    )
    db.add(create_user_model)
    db.commit()

    create_user_role_model = UserRole(
        user_id=create_user_model.id,
        role_id=2,
    )
    db.add(create_user_role_model)

    create_participant_model = Participant(
        user_id=create_user_model.id,
        country_id=country.id,
        title=item["TITLE"],
        institution=item["INSTITUTION"],
    )
    db.add(create_participant_model)

    create_user_event_model = UserEvent(
        user_id=create_user_model.id,
        event_id=eventID,
        participant_category=item["PARTICIPANT_CATEGORY"],
        confirm_attendance=int(item["CONFIRM_ATTENDANCE"]),
        event_payment=int(item["EVENT_PAYMENT"]),
        confirmation_code=item["PAYMENT_CONFIRMATION_CODE"],
    )
    db.add(create_user_event_model)

    db.commit()
    utils.new_account_email(item["EMAIL"], item["FIRSTNAME"], password)
    return 1


@router.post("/upload_file/")
async def upload_file(
    user: user_dependency,
    file: UploadFile = File(...),
    resource_title: str = Form(...),
    access_level: str = Form(...),
    event_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
            event_resource_file_model = EventResourceFile(
                event_id=event_id,
                filename=file.filename,
                filepath=file_location,
                file_name=resource_title,
                access_level=access_level,
            )
        db.add(event_resource_file_model)
        db.commit()
        db.refresh(event_resource_file_model)
        return JSONResponse(
            content={
                "status": "success",
                "message": f"File '{file.filename}' uploaded with access level '{access_level}'",
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/add_event_link/")
async def add_event_link(
    event_link_schema: EventLinkSchema,
    user: user_dependency,
    db: Session = Depends(get_db),
):
    security.secureAccess("ADD_EVENT", user["id"], db)
    event_link_model = EventLink(
        event_id=event_link_schema.event_id,
        link_name=event_link_schema.link_name,
        link=event_link_schema.link,
        access_level=event_link_schema.access_level,
    )

    db.add(event_link_model)
    db.commit()
    db.refresh(event_link_model)
    return event_link_model


@router.get("/user/{user_id}/event/{event_id}")
async def user_event(
    user_id: int,
    event_id: int,
    db: Session = Depends(get_db),
):
    user_event = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == user_id, UserEvent.event_id == event_id)
        .first()
    )
    if user_event is None:
        raise HTTPException(
            status_code=404,
            detail=f"User event with event id {event_id} and User id {user_id} does not exist",
        )
    else:
        participant = (
            db.query(Participant).filter(Participant.user_id == user_id).first()
        )
        attendance = (
            db.query(UserEventAttendance)
            .filter(
                UserEventAttendance.user_id == user_id,
                UserEventAttendance.event_id == event_id,
            )
            .all()
        )
        return {
            "user_event": {
                "event_id": user_event.event.id,
                "event": user_event.event.event,
                "event_type": user_event.event.event_type.event_type,
                "event_country": user_event.event.country.country,
                "event_organiser": user_event.event.organiser.organiser,
                "location": user_event.event.location,
                "capacity": user_event.event.capacity,
                "description": user_event.event.description,
                "start_date": user_event.event.start_date,
                "end_date": user_event.event.end_date,
                "registration_start_date": user_event.event.registration_start_date,
                "registration_end_date": user_event.event.registration_end_date,
                "user_id": user_event.user_id,
                "title": participant.title,
                "firstname": user_event.users.firstname,
                "lastname": user_event.users.lastname,
                "phone": user_event.users.phone,
                "email": user_event.users.email,
                "institution": participant.institution,
                "participant_country": participant.country.country,
                "participant_category": user_event.participant_category,
                "confirm_attendance": user_event.confirm_attendance,
                "event_badge": user_event.event_badge,
                "event_payment": user_event.event_payment,
                "confirmation_code": user_event.confirmation_code,
            },
            "attendance": [{"date": attendance.date} for attendance in attendance],
        }


@router.post("/confirm_event_payment/")
async def confirm_event_payment(
    event_payment_schema: EventPaymentSchema,
    db: Session = Depends(get_db),
):
    user_event_model = (
        db.query(UserEvent)
        .filter(
            UserEvent.user_id == event_payment_schema.user_id,
            UserEvent.event_id == event_payment_schema.event_id,
        )
        .first()
    )

    user_event_model.confirm_attendance = 1
    user_event_model.event_payment = 1
    user_event_model.confirmation_code = "".join(
        random.choices(string.ascii_letters, k=30)
    )
    db.commit()
    db.refresh(user_event_model)
    return user_event_model


@router.get("/event/{event_id}")
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = get_object(event_id, db, Event)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "event": {
            "id": event.id,
            "event": event.event,
            "event_type": event.event_type.event_type,
            "description": event.description,
            "country": event.country.country,
            "organiser": event.organiser.organiser,
            "location": event.location,
            "capacity": event.capacity,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "registration_start_date": event.registration_start_date,
            "registration_end_date": event.registration_end_date,
        }
    }


@router.post("/confirm_event_attendance/")
async def confirm_event_attendance(
    event_attendance_schema: EventAttendanceSchema,
    db: Session = Depends(get_db),
):
    user_event = (
        db.query(UserEvent)
        .filter(
            UserEvent.user_id == event_attendance_schema.user_id,
            UserEvent.event_id == event_attendance_schema.event_id,
        )
        .first()
    )
    if user_event is None:
        raise HTTPException(
            status_code=404,
            detail="Incorrect ID number used, use the identification # on your badge",
        )

    attendance_status = (
        db.query(UserEventAttendance)
        .filter(
            UserEventAttendance.user_id == event_attendance_schema.user_id,
            UserEventAttendance.event_id == event_attendance_schema.event_id,
            func.date(UserEventAttendance.date) == datetime.now().date(),
        )
        .first()
    )
    if attendance_status:
        raise HTTPException(
            status_code=409, detail="Already registered attendance for today"
        )

    user_event_attendance_model = UserEventAttendance(
        user_id=event_attendance_schema.user_id,
        event_id=event_attendance_schema.event_id,
        date=datetime.now(),
    )
    db.add(user_event_attendance_model)
    try:
        db.commit()
        db.refresh(user_event_attendance_model)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return user_event_attendance_model

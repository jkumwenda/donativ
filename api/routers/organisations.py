import math
from sqlalchemy import or_
from fastapi import status, HTTPException
from typing import Annotated
from core.database import get_db
from sqlalchemy.orm import Session
import utils.mailer_util as mailer_util
from datetime import datetime, timedelta
from dependencies.auth_dependency import Auth
from dependencies.dependency import Dependency
from dependencies.auth_dependency import get_current_user
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from models.models import Organisation, OrganisationVerificationRequest, User, OrganisationApprovalStatus
from schemas.donativ import OrganisationSchema, OrganisationIDSchema, OrganisationApprovalSchema


router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_dependency(db: Session = Depends(get_db)) -> Dependency:
    return Dependency(db)


def get_auth_dependency(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)


def get_object(id, db, model):
    data = db.query(model).filter(model.id == id).filter(
        model.deleted_at is None).first()
    if data is None:
        raise HTTPException(
            status_code=404, detail=f"ID {id} : Does not exist")
    return data


@router.get("/")
async def get_organisations(
    request: Request,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_ORGANISATION", current_user['user_id'])
    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'VIEW_ORGANISATIONS',
        current_user['username'],
        client_ip,
        "Get all organisations"
    )

    search_filter = or_(
        Organisation.organisation.ilike(f"%{search}%"),
        Organisation.organisation_type.ilike(f"%{search}%"),
        Organisation.sector.ilike(f"%{search}%"),
        Organisation.email.ilike(f"%{search}%"),
        Organisation.phone_number.ilike(f"%{search}%")
    )

    organisations_query = db.query(Organisation).filter(
        search_filter, Organisation.deleted_at == None)

    total_count = organisations_query.count()
    organisations = organisations_query.offset(
        (skip - 1) * limit).limit(limit).all()

    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": organisations}


@ router.post("/")
async def add_organisation(
    request: Request,
    organisation_schema: OrganisationSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("ADD_ORGANISATION", current_user["user_id"])

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ADD_ORGANISATION',
        current_user['username'],
        client_ip,
        organisation_schema.organisation
    )

    create_organisation_model = Organisation(
        country_id=organisation_schema.country_id,
        created_by_id=current_user["user_id"],
        organisation=organisation_schema.organisation,
        organisation_type=organisation_schema.organisation_type,
        sector=organisation_schema.sector,
        address=organisation_schema.address,
        city=organisation_schema.city,
        email=organisation_schema.email,
        phone_number=organisation_schema.phone_number,
        is_donor=organisation_schema.is_donor,
        is_recipient=organisation_schema.is_recipient
    )

    db.add(create_organisation_model)
    db.commit()
    return organisation_schema


@ router.get("/{organisation_id}")
async def get_organisation(
    request: Request,
    organisation_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access("VIEW_ORGANISATION", current_user["user_id"])
    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user['user_id'],
        'VIEW_ORGANISATION',
        current_user['username'],
        client_ip,
        f"View organisation id {organisation_id} and associated permissions"
    )

    if organisation := get_object(organisation_id, db, Organisation):
        return {
            "organisation": {
                "id": organisation.id,
                "organisation": organisation.organisation,
                "country_id": organisation.country_id,
                "country": organisation.country.country,
                "organisation_type": organisation.organisation_type,
                "sector": organisation.sector,
                "address": organisation.address,
                "city": organisation.city,
                "email": organisation.email,
                "phone_number": organisation.phone_number,
                "is_donor": organisation.is_donor,
                "is_recipient": organisation.is_recipient

            },
            "registration": [
                {
                    "id": organisation_registration.id,
                    "registration_number": organisation_registration.registration_number,
                    "registration_date": organisation_registration.registration_date,
                    "founders": organisation_registration.founders,
                }
                for organisation_registration in organisation.registrations
            ],
            "documents": [
                {
                    "id": document.id,
                    "document_type": document.document_type,
                    "path": document.path,
                }
                for document in organisation.documents
            ],
            "verification": [
                {
                    "id": verification.id,
                    "submitted_by": verification.user,
                    "expires_at": verification.expires_at,
                    "is_approved": verification.is_approved,
                    "comment": verification.comment,
                }
                for verification in organisation.verifications
            ],
        }
    else:
        raise HTTPException(status_code=404, detail="organisation not found")


@ router.put("/{organisation_id}")
async def update_organisation(
    request: Request,
    organisation_id: int,
    current_user: user_dependency,
    organisation_schema: OrganisationSchema,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access(
        "UPDATE_ORGANISATION", current_user["user_id"])

    client_ip = dependency.request_ip(request)

    dependency.log_activity(
        current_user['user_id'],
        'UPDATE_ORGANISATION',
        current_user['username'],
        client_ip,
        f"Update organisation id {organisation_id}"
    )

    organisation_model = get_object(organisation_id, db, Organisation)

    organisation_model.country_id = organisation_schema.country_id
    organisation_model.organisation = organisation_schema.organisation
    organisation_model.organisation_type = organisation_schema.organisation_type
    organisation_model.sector = organisation_schema.sector
    organisation_model.address = organisation_schema.address
    organisation_model.city = organisation_schema.city
    organisation_model.email = organisation_schema.email
    organisation_model.phone_number = organisation_schema.phone_number
    organisation_model.is_donor = organisation_schema.is_donor
    organisation_model.is_recipient = organisation_schema.is_recipient

    db.commit()
    db.refresh(organisation_model)
    return organisation_schema


@ router.delete("/{organisation_id}")
async def delete_organisation(
    request: Request,
    organisation_id: int,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency)
):
    auth_dependency.secure_access(
        "DELETE_ORGANISATION", current_user["user_id"])

    dependency.cascade_soft_delete_recursive(Organisation, organisation_id)

    client_ip = dependency.request_ip(request)
    organisation = get_object(organisation_id, db, Organisation)

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'DELETE_ORGANISATION',
        current_user['username'],
        client_ip,
        f"Delete organisation id {organisation_id} organisation {organisation.organisation}"
    )
    return {"detail": "organisation Successfully deleted"}


@ router.post("/verification_request/")
async def verification_request(
    request: Request,
    organisation_id_schema: OrganisationIDSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
):
    organisation = db.query(Organisation).filter(Organisation.id == organisation_id_schema.organisation_id,
                                                 Organisation.created_by_id == current_user["user_id"]).filter().first()

    user = db.query(User).filter(User.id == current_user['user_id']).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="You do not have permission to perfom this action",
        )

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ORGANISATION_VERIFICATION_REQUEST',
        current_user['username'],
        client_ip,
        f"The organisation ID {organisation_id_schema.organisation_id}"
    )

    create_organisation_verification_request_model = OrganisationVerificationRequest(
        submitted_by_id=current_user['user_id'],
        organisation_id=organisation_id_schema.organisation_id,
        expires_at=datetime.now() + timedelta(hours=94),
    )

    db.add(create_organisation_verification_request_model)
    db.commit()

    mailer_util.organisation_verification_request_email(
        current_user['username'], user.firstname, organisation)
    return {"message": "Organisation verification request submitted successfully"}


@ router.post("/approval_status/")
async def approval_status(
    request: Request,
    organisation_approval_schema: OrganisationApprovalSchema,
    current_user: user_dependency,
    db: Session = Depends(get_db),
    dependency: Dependency = Depends(get_dependency),
    auth_dependency: Auth = Depends(get_auth_dependency),
):
    auth_dependency.secure_access(
        "ORGANISATION_VERIFICATION_APPROVAL", current_user["user_id"])

    verification_request = db.query(OrganisationVerificationRequest).filter(
        OrganisationVerificationRequest.organisation_id == organisation_approval_schema.organisation_id).filter().first()

    user = db.query(User).filter(User.id == current_user['user_id']).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="This verification request does not exists",
        )

    client_ip = dependency.request_ip(request)
    dependency.log_activity(
        current_user['user_id'],
        'ORGANISATION_VERIFICATION_REQUEST',
        current_user['username'],
        client_ip,
        f"The organisation ID {verification_request.organisations.organisation}"
    )

    create_organisation_approval_status_model = OrganisationApprovalStatus(
        approved_by_id=current_user['user_id'],
        organisation_id=organisation_approval_schema.organisation_id,
        is_approved=organisation_approval_schema.is_approved,
        comment=organisation_approval_schema.comment,
    )

    db.add(create_organisation_approval_status_model)
    db.commit()

    mailer_util.organisation_approval_status_email(
        current_user['username'], user.firstname, verification_request.organisations, organisation_approval_schema.is_approved)
    return {"message": "Organisation verification request status processed successfully"}

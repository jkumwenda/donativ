from pydantic import BaseModel
from datetime import date, datetime


class UserSchema(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: str


class ResertPasswordSchema(BaseModel):
    username: str


class PasswordSchema(BaseModel):
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class RoleSchema(BaseModel):
    role: str
    description: str


class UserRoleSchema(BaseModel):
    user_id: int
    role_id: int


class PermissionSchema(BaseModel):
    permission: str
    permission_code: str


class RolePermissionSchema(BaseModel):
    role_id: int
    permission_id: int


class CountrySchema(BaseModel):
    country: str
    short_code: str
    phone_code: str


class EventTypeSchema(BaseModel):
    event_type: str
    description: str


class OrganiserSchema(BaseModel):
    organiser: str
    description: str


class EventSchema(BaseModel):
    event_type_id: int
    country_id: int
    organiser_id: int
    event: str
    location: str
    capacity: int
    description: str
    start_date: datetime
    end_date: datetime
    registration_start_date: datetime
    registration_end_date: datetime


class EventRegistrationSchema(BaseModel):
    event_id: int
    participant_category: str


class ParticipantSchema(BaseModel):
    country_id: int
    title: str
    firstname: str
    lastname: str
    phone: str
    email: str
    institution: str


class PaymentSchema(BaseModel):
    event_id: int
    user_id: int
    transaction_code: str


class OnlinePaymentSchema(BaseModel):
    event_id: int
    card_number: int
    csv: str
    email: str
    card_holder: str
    year: int
    month: int


class UserEventSchema(BaseModel):
    user_id: int
    event_id: int


class EventLinkSchema(BaseModel):
    event_id: int
    link_name: str
    link: str
    access_level: str


class EventPaymentSchema(BaseModel):
    event_id: int
    user_id: int
    private_key: str


class EventAttendanceSchema(BaseModel):
    event_id: int
    user_id: int

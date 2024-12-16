from pydantic import BaseModel, EmailStr, field_validator
import re


class UserSchema(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: EmailStr

    @field_validator('phone')
    def validate_phone(cls, value):
        phone_regex = r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
        if not re.match(phone_regex, value):
            raise ValueError('Invalid phone number format')
        return value


class EmailSchema(BaseModel):
    email: EmailStr


class AuthSchema(BaseModel):
    username: EmailStr
    password: str


class PasswordResetSchema(BaseModel):
    password: str
    rest_token: str


class VerificationTokenSchema(BaseModel):
    verification_token: str


class RoleSchema(BaseModel):
    role: str
    description: str


class UserRoleSchema(BaseModel):
    user_id: int
    role_id: int


class PermissionSchema(BaseModel):
    permission: str
    system_code: str
    permission_code: str


class RolePermissionSchema(BaseModel):
    role_id: int
    permission_id: int


class CountrySchema(BaseModel):
    country: str
    short_code: str
    phone_code: str


class OrganisationSchema(BaseModel):
    country_id: int
    organisation: str
    organisation_type: str
    sector: str
    address: str
    city: str
    email: EmailStr
    phone_number: str
    is_donor: int
    is_recipient: int


class OrganisationIDSchema(BaseModel):
    organisation_id: int


class OrganisationApprovalSchema(BaseModel):
    organisation_id: int
    is_approved: str
    comment: str

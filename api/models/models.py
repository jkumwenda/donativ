from enum import Enum as PyEnum
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    TIMESTAMP,
    UniqueConstraint, JSON, Enum, Index
)
from datetime import datetime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class OrganisationType(PyEnum):
    Non_profit = "Non_profit"
    Corporation = "Corporation"
    Government = "Government"
    Other = "Other"


class SectorType(PyEnum):
    Technology = "Technology"
    Education = "Education"
    Healthcare = "Healthcare"
    Finance = "Finance"
    Other = "Other"


class DocumentType(PyEnum):
    Certificate = "Certificate"
    Agreement = "Agreement"
    License = "License"
    Other = "Other"


class OrganisationStatus(PyEnum):
    Pending = "Pending"
    Approved = "Approved"
    Denied = "Denied"


class BaseWithSoftDelete(Base):
    __abstract__ = True

    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    @classmethod
    def filter_deleted(cls, query):
        return query.filter(cls.deleted_at is None)


class User(BaseWithSoftDelete):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(45), nullable=False)
    lastname = Column(String(45), nullable=False)
    phone = Column(String(25), nullable=False, unique=True)
    email = Column(String(45), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    verified = Column(Boolean, nullable=False, server_default="False")
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())

    user_roles = relationship(
        "UserRole", back_populates="user"
    )

    organisations = relationship(
        "Organisation", back_populates="users"
    )

    __table_args__ = (
        Index('ix_user', 'deleted_at', 'email', 'phone', 'id'),
    )

    def __repr__(self):
        return f"<User {self.id}>"


class Role(BaseWithSoftDelete):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(
        String(45),
        unique=True,
    )
    description = Column(
        Text,
        nullable=False,
    )
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user_roles = relationship(
        "UserRole", back_populates="role")

    role_permissions = relationship(
        "RolePermission", back_populates="role")

    __table_args__ = (
        Index('ix_role', 'role', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Role {self.id}"


class UserRole(BaseWithSoftDelete):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        UniqueConstraint(user_id, role_id, name="user_id_role_id"),
        Index('ix_user_role', 'user_id', 'role_id', 'deleted_at'),
    )

    def __repr__(self):
        return f"<UserRole user_id={self.user_id}, role_id={self.role_id}>"


class Permission(BaseWithSoftDelete):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    permission = Column(String(45), unique=True, nullable=False,)
    permission_code = Column(String(45), unique=True, nullable=False)
    system_code = Column(String(45), unique=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    role_permissions = relationship(
        "RolePermission", back_populates="permission")

    __table_args__ = (
        Index('ix_permission', 'permission', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Permission {self.permission}"


class RolePermission(BaseWithSoftDelete):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey(
        "permission.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id",
                         name="role_id_permission_id"),
        Index('ix_role_permission', 'role_id', 'permission_id', 'deleted_at'),
    )

    def __repr__(self):
        return f"<RolePermission role_id={self.role_id}, permission_id={self.permission_id}>"


class Country(BaseWithSoftDelete):
    __tablename__ = "country"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), unique=True, index=True)
    short_code = Column(String(5), unique=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    organisations = relationship(
        "Organisation", back_populates="country")

    Index('ix_country_deleted_at', 'country', 'deleted_at')

    def __repr__(self):
        return f"<Country {self.id}>"


class ActivityLog(BaseWithSoftDelete):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=True)
    action = Column(String, nullable=False)
    target = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_activity_log', 'action', 'deleted_at'),
    )

    def __repr__(self):
        return f"<ActivityLog {self.id}>"


class PasswordReset(BaseWithSoftDelete):
    __tablename__ = "password_reset"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    reset_token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_password_reset', 'deleted_at'),
    )

    def __repr__(self):
        return f"<PasswordReset {self.id}>"


class AccountVerification(BaseWithSoftDelete):
    __tablename__ = "account_verification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    verification_token = Column(
        String, nullable=False, unique=True, index=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_account_verification', 'deleted_at'),
    )

    def __repr__(self):
        return f"<AccountVerification {self.id}>"


class Organisation(BaseWithSoftDelete):
    __tablename__ = "organisation"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey(
        "country.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    organisation = Column(String(200), unique=False, nullable=False)
    organisation_type = Column(Enum(OrganisationType), nullable=False)
    sector = Column(Enum(SectorType), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_donor = Column(Boolean, default=False)
    is_recipient = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('organisation', 'country_id',
                         name='uix_organisation_country'),
        Index('ix_organisation_country', 'organisation',
              'country_id', 'deleted_at')
    )

    country = relationship(
        "Country", back_populates="organisations")
    users = relationship(
        "User", back_populates="organisations")
    registrations = relationship(
        "OrganisationRegistration", back_populates="organisations")
    documents = relationship(
        "OrganisationDocument", back_populates="organisations")
    verification_requests = relationship(
        "OrganisationVerificationRequest", back_populates="organisations")
    approval_statuses = relationship(
        "OrganisationApprovalStatus", back_populates="organisations")

    def __repr__(self):
        return f"<Organisation id={self.id}, name={self.organisation}, country_id={self.country_id}>"


class OrganisationRegistration(BaseWithSoftDelete):
    __tablename__ = "organisation_registration"

    id = Column(Integer, primary_key=True, index=True)
    organisation_id = Column(Integer, ForeignKey(
        "organisation.id", ondelete="CASCADE"), nullable=False)
    registration_number = Column(String(45), unique=True, nullable=False)
    registration_date = Column(TIMESTAMP(timezone=True), nullable=False)
    founders = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    organisations = relationship(
        "Organisation", back_populates="registrations")

    __table_args__ = (
        Index('ix_organisation_registration',
              'registration_number', 'deleted_at'),
    )

    def __repr__(self):
        return f"<OrganisationRegistration registration_number={self.registration_number}>"


class OrganisationDocument(BaseWithSoftDelete):
    __tablename__ = "organisation_document"

    id = Column(Integer, primary_key=True, index=True)
    organisation_id = Column(Integer, ForeignKey(
        "organisation.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    path = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    organisations = relationship("Organisation", back_populates="documents")

    __table_args__ = (
        Index('ix_organisation_document',
              'document_type', 'deleted_at'),
    )

    def __repr__(self):
        return f"<OrganisationDocument document_type={self.document_type}, path={self.path}>"


class OrganisationVerificationRequest(BaseWithSoftDelete):
    __tablename__ = "organisation_verification_request"

    id = Column(Integer, primary_key=True, index=True)
    submitted_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    organisation_id = Column(Integer, ForeignKey(
        "organisation.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    organisations = relationship(
        "Organisation", back_populates="verification_requests")

    __table_args__ = (
        Index('ix_organisation_verification_request',
              'organisation_id', 'deleted_at'),
    )

    @validates("expires_at")
    def validate_expires_at(self, key, expires_at):
        # Validate if expires_at is in the future
        if expires_at < datetime.now():
            raise ValueError("Expires date cannot be in the past.")
        return expires_at

    def __repr__(self):
        return f"<OrganisationVerificationRequest id={self.id}, is_verified={self.is_verified}>"


class OrganisationApprovalStatus(BaseWithSoftDelete):
    __tablename__ = "organisation_approval_status"

    id = Column(Integer, primary_key=True, index=True)
    approved_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    organisation_id = Column(Integer, ForeignKey(
        "organisation.id", ondelete="CASCADE"), nullable=False)
    is_approved = Column(Enum(OrganisationStatus), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    organisations = relationship(
        "Organisation", back_populates="approval_statuses")

    __table_args__ = (
        Index('ix_organisation_approval_status',
              'organisation_id', 'deleted_at'),
    )

    def __repr__(self):
        return f"<OrganisationApprovalStatus id={self.id}, is_approved={self.is_approved}>"

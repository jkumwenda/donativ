from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    TIMESTAMP,
    DATE,
    text,
    DATETIME,
    UniqueConstraint,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(45), nullable=False)
    lastname = Column(String(45), nullable=False)
    phone = Column(String(25), nullable=False, unique=True)
    email = Column(String(45), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    verified = Column(Boolean, nullable=False, server_default="False")
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    user_role = relationship("UserRole", back_populates="users")
    participant = relationship("Participant", back_populates="users")
    user_event = relationship("UserEvent", back_populates="users")
    user_event_attendance = relationship("UserEventAttendance", back_populates="users")

    def __repr__(self):
        return f"<Users {self.id}>"


class Role(Base):
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
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    user_role = relationship("UserRole", back_populates="role")
    role_permission = relationship("RolePermission", back_populates="role")

    def __repr__(self):
        return f"<Role {self.role}"


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    __table_args__ = (UniqueConstraint(user_id, role_id, name="user_id_role_id"),)
    users = relationship("Users", back_populates="user_role")
    role = relationship("Role", back_populates="user_role")

    def __repr__(self):
        return f"<UserRole {self.user_role}"


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    permission = Column(
        String(45),
        unique=True,
        nullable=False,
    )
    permission_code = Column(
        String(45),
        unique=True,
        nullable=False,
    )
    system_code = Column(
        String(45),
        unique=False,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    role_permission = relationship("RolePermission", back_populates="permission")

    def __repr__(self):
        return f"<Permission {self.permission}"


class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.now,
    )
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="role_id_permission_id"),
    )
    role = relationship("Role", back_populates="role_permission")
    permission = relationship("Permission", back_populates="role_permission")

    def __repr__(self):
        return f"<RolePermission {self.role_permission}"


class Country(Base):
    __tablename__ = "country"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), unique=True, index=True)
    short_code = Column(String(5), unique=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    participant = relationship("Participant", back_populates="country")
    event = relationship("Event", back_populates="country")

    def __repr__(self):
        return f"<Country {self.id}>"


class Organiser(Base):
    __tablename__ = "organiser"
    id = Column(Integer, primary_key=True, index=True)
    organiser = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    event = relationship("Event", back_populates="organiser")

    def __repr__(self):
        return f"<Organiser {self.id}>"


class EventType(Base):
    __tablename__ = "event_type"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    event = relationship("Event", back_populates="event_type")

    def __repr__(self):
        return f"<EventType {self.id}>"


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, index=True)
    event_type_id = Column(Integer, ForeignKey("event_type.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    organiser_id = Column(Integer, ForeignKey("organiser.id"), nullable=False)
    event = Column(String(100), unique=True, index=True)
    location = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=True)
    capacity = Column(Text, nullable=True)
    start_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    end_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    registration_start_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    registration_end_date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    country = relationship("Country", back_populates="event")
    event_type = relationship("EventType", back_populates="event")
    organiser = relationship("Organiser", back_populates="event")
    user_event = relationship("UserEvent", back_populates="event")
    event_resource_file = relationship("EventResourceFile", back_populates="event")
    event_link = relationship("EventLink", back_populates="event")
    user_event_attendance = relationship("UserEventAttendance", back_populates="event")

    def __repr__(self):
        return f"<Event {self.id}>"


class UserEvent(Base):
    __tablename__ = "user_event"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    participant_category = Column(String(100), unique=False, index=True)
    confirm_attendance = Column(Boolean, nullable=False, default=False)
    event_badge = Column(Boolean, nullable=False, default=False)
    event_payment = Column(Boolean, nullable=False, default=False)
    confirmation_code = Column(String(200), unique=False, index=True, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    users = relationship("Users", back_populates="user_event")
    event = relationship("Event", back_populates="user_event")

    def __repr__(self):
        return f"<UserEvent {self.id}>"


class Participant(Base):
    __tablename__ = "participant"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    title = Column(String(10), index=True)
    institution = Column(String(200), index=True)
    picture = Column(String(200), index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    users = relationship("Users", back_populates="participant")
    country = relationship("Country", back_populates="participant")

    def __repr__(self):
        return f"<Participant {self.id}>"


class EventResourceFile(Base):
    __tablename__ = "event_resource_file"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    filename = Column(String(100), unique=False, index=True)
    filepath = Column(String(250), unique=False, index=True)
    file_name = Column(String(250), unique=False, index=True)
    access_level = Column(String(50), unique=False, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    event = relationship("Event", back_populates="event_resource_file")

    def __repr__(self):
        return f"<EventResourceFile {self.id}>"


class EventLink(Base):
    __tablename__ = "event_link"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    link_name = Column(String(250), unique=False, index=True)
    link = Column(String(250), unique=False, index=True)
    access_level = Column(String(50), unique=False, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    event = relationship("Event", back_populates="event_link")

    def __repr__(self):
        return f"<EventLink {self.id}>"


class UserEventAttendance(Base):
    __tablename__ = "user_event_attendance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    date = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
        onupdate=datetime.now,
    )
    event = relationship("Event", back_populates="user_event_attendance")
    users = relationship("Users", back_populates="user_event_attendance")

    def __repr__(self):
        return f"<UserEventAttendance {self.id}>"

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    devices = relationship("Device", back_populates="owner", cascade="all, delete-orphan")
    pairing_codes = relationship("PairingCode", back_populates="owner", cascade="all, delete-orphan")
    command_records = relationship("CommandRecord", back_populates="owner", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String(64), primary_key=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64), nullable=False, default="computer")  # computer, phone, iot, sensor
    platform = Column(String(64), nullable=False, default="windows")  # windows, android, linux, esp32
    status = Column(String(32), nullable=False, default="offline")  # online, offline, connecting
    last_seen = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    capabilities = Column(JSON, nullable=False, default=list)  # list of strings
    version = Column(String(32), default="1.0.0")
    connection_id = Column(String(64), nullable=True)
    device_token = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    owner = relationship("User", back_populates="devices")
    command_records = relationship("CommandRecord", back_populates="device")


class PairingCode(Base):
    __tablename__ = "pairing_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(16), unique=True, index=True, nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    owner = relationship("User", back_populates="pairing_codes")


class CommandRecord(Base):
    __tablename__ = "command_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(64), ForeignKey("devices.device_id", ondelete="SET NULL"), nullable=True, index=True)
    query = Column(Text, nullable=False)
    action = Column(String(64), nullable=True)
    device_name = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="completed")  # completed, failed, cancelled, pending
    result = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    owner = relationship("User", back_populates="command_records")
    device = relationship("Device", back_populates="command_records")

import re
import uuid
from datetime import datetime
from . import Base
from .. import bcrypt
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
)


class User(Base):
    __tablename__ = "user"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4())
    wallet_address = Column(String(42), index=True)
    fname = Column(String(64))
    lname = Column(String(64))
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128))
    email = Column(String(120), index=True)
    registered_on = Column(DateTime)

    miners = relationship("Miner",
                          back_populates="user",
                          cascade="all, delete-orphan")
    stats = relationship("UserStat",
                         back_populates="user",
                         cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # used for updating a users name, etc.
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @validates('username')
    def validate_username(self, key, username):
        session = Session.object_session(self)
        if not username:
            raise AssertionError('No username provided')
        if len(username) < 5 or len(username) > 20:
            raise AssertionError('Username must be between 5 and 20 characters')
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('No email provided')
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Provided email is not an email address')
        return email

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class UserStat(Base):
    __tablename__ = "userStat"

    time = Column(DateTime, default=datetime.utcnow(), primary_key=True)
    user_id = Column(UNIQUEIDENTIFIER,
                     ForeignKey("user.id",
                                ondelete="CASCADE"),
                     primary_key=True)
    user = relationship("User", back_populates="stats")

    balance = Column(Float)
    est_revenue = Column(Float)
    valid_shares = Column(Integer)
    stale_shares = Column(Integer)
    invalid_shares = Column(Integer)
    round_share_percent = Column(Float)
    effective_hashrate = Column(Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

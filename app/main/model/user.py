import re
from datetime import datetime
from . import Base
from .. import bcrypt
from sqlalchemy.orm import relationship, validates
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

    wallet_addr = Column(String(42), primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True)
    password_hash = Column(String(128))

    fname = Column(String(64))
    lname = Column(String(64))

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
        if not username:
            raise AssertionError('No username provided')
        if User.query.filter(User.username == username).first():
            raise AssertionError('Username is already in use')
        if len(username) < 5 or len(username) > 20:
            raise AssertionError('Username must be between 5 and 20 characters')
        return username @ validates('email')

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

    time = Column(DateTime, default=datetime.now(), primary_key=True)
    wallet_addr = Column(String(42),
                         ForeignKey("user.wallet_addr",
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
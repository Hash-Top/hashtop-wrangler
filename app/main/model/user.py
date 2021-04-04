from datetime import datetime
from . import Base
from sqlalchemy.orm import relationship
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
    fname = Column(String)
    lname = Column(String)

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
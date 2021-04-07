import uuid
from . import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship, validates
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    UniqueConstraint,
)


class Miner(Base):
    __tablename__ = "miner"
    __table_args__ = (
        # miner names are unique per user
        UniqueConstraint("user_id", "name"),
    )

    id = Column(UNIQUEIDENTIFIER,
                primary_key=True,
                default=uuid.uuid4())
    name = Column(String(64))
    user_id = Column(UNIQUEIDENTIFIER,
                     ForeignKey("user.id",
                                ondelete="CASCADE"),
                     primary_key=True)
    user = relationship("User", back_populates="miners")

    gpus = relationship("Gpu",
                        back_populates="miner",
                        cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        def update(self, **kwargs):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)


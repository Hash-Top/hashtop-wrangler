import uuid
from . import Base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
)

class Miner(Base):
    __tablename__ = "miner"

    id = Column(UNIQUEIDENTIFIER,
                primary_key=True,
                default=uuid.uuid4())
    wallet_addr = Column(String(42),
                         ForeignKey("user.wallet_addr",
                                    ondelete="CASCADE"))
    user = relationship("User", back_populates="miners")

    gpus = relationship("Gpu",
                        back_populates="miner",
                        cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
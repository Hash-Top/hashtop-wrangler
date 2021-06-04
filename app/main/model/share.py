import enum
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKeyConstraint,
    Enum
)
from . import Base


class ShareType(enum.Enum):
    valid = "valid share"
    invalid = "invalid share"
    stale = "stale share (reported by pool)"

    def __str__(self):
        return self.name


class Share(Base):
    __tablename__ = "share"
    __table_args__ = (
        ForeignKeyConstraint(
            ["miner_id", "gpu_no"], ["gpu.miner_id", "gpu.gpu_no"],
            ondelete="CASCADE"
        ),
    )

    time = Column(DateTime, default=datetime.now(), primary_key=True)

    # don't need backpopulates because we only ever insert into this table
    miner_id = Column(UNIQUEIDENTIFIER, primary_key=True)
    gpu_no = Column(Integer, primary_key=True)

    type = Column(Enum(ShareType), primary_key=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

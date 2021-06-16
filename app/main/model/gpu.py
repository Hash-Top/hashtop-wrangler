from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from . import Base


class Gpu(Base):
    __tablename__ = "gpu"
    __table_args__ = (
        UniqueConstraint("miner_id", "gpu_no"),
    )

    gpu_no = Column(Integer, primary_key=True)
    gpu_name = Column(String, primary_key=False)
    miner_id = Column(UNIQUEIDENTIFIER,
                      ForeignKey("miner.id",
                                 ondelete="CASCADE"),
                      primary_key=True)
    miner = relationship("Miner", back_populates="gpus")

    healths = relationship("Health",
                           cascade="all, delete-orphan")

    shares = relationship("Share",
                          cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Health(Base):
    __tablename__ = "health"
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
    gpu_name = Column(String, primary_key=False)

    fan_speed = Column(Integer, default=0)
    temperature = Column(Integer, default=0)
    power_draw = Column(Integer, default=0)
    power_limit = Column(Integer, default=0)
    hashrate = Column(Float, default=0)
    core = Column(Integer, default=0)
    memory = Column(Integer, default=0)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

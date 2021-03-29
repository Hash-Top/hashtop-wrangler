from dotenv import load_dotenv
import uuid
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    ForeignKeyConstraint,

)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
)
import urllib
import os

load_dotenv()
AZURE_CONNECT_STRING = os.getenv("AZURE_CONNECT_STRING")
params = urllib.parse.quote(AZURE_CONNECT_STRING)
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine = create_engine(conn_str,echo=True)


Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4())
    fname = Column(String)
    lname = Column(String)
    wallet_addr = Column(String(42))

    miners = relationship("Miner", back_populates="user")
    stats = relationship("UserStat", back_populates="user")

class UserStat(Base):
    __tablename__ = "userStat"

    time = Column(DateTime, primary_key=True)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", back_populates="stats")

    balance = Column(Float)
    est_revenue = Column(Float)
    valid_shares = Column(Integer)
    stale_shares = Column(Integer)
    invalid_shares = Column(Integer)
    round_share_percent = Column(Float)
    hash_rate = Column(Float)

class Miner(Base):
    __tablename__ = "miner"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4())
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("user.id"))
    user = relationship("User", back_populates="miners")

    gpus = relationship("Gpu", back_populates="miner")

class Gpu(Base):
    __tablename__ = "gpu"

    miner_id = Column(UNIQUEIDENTIFIER, ForeignKey("miner.id"), primary_key=True)
    gpu_no = Column(Integer, primary_key=True)
    miner = relationship("Miner", back_populates="gpus")


class Health(Base):
    __tablename__ = "health"
    __table_args__ = (
        ForeignKeyConstraint(
            ["miner_id", "gpu_no"], ["gpu.miner_id", "gpu.gpu_no"]
        ),
    )

    # don't need backpopulates because we only ever insert into this table
    miner_id = Column(UNIQUEIDENTIFIER, primary_key=True)
    gpu_no = Column(Integer, primary_key=True)
    parent = relationship(
        "Gpu",
        foreign_keys="[Health.miner_id, Health.gpu_no]",
    )

    time = Column(DateTime)
    temperature = Column(Integer)


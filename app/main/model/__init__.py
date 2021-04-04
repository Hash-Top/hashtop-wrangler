from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base()

from .user import User, UserStat
from .miner import Miner
from .gpu import Gpu, Health

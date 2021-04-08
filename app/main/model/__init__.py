import os
from sqlalchemy.orm import declarative_base, Session, scoped_session, sessionmaker
from sqlalchemy import MetaData, create_engine
from .. import config_env

metadata = MetaData()
Base = declarative_base()

# create a global session to user when querying inside of model class
engine = create_engine(config_env.SQLALCHEMY_DATABASE_URI)
global_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
Base.query = global_session.query_property()

from .user import User, UserStat
from .miner import Miner
from .gpu import Gpu, Health
from .blacklist import BlacklistToken

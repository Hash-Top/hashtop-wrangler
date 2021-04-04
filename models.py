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
    MetaData,
)

from sqlalchemy.orm import (
    declarative_base,
    relationship,
)
import urllib
import os
from datetime import datetime

load_dotenv()
AZURE_CONNECT_STRING = os.getenv("AZURE_CONNECT_STRING")
params = urllib.parse.quote(AZURE_CONNECT_STRING)
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine = create_engine(conn_str,echo=True)

metadata = MetaData()
Base = declarative_base()







#Base.metadata.create_all(engine)
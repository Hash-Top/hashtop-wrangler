import os
import urllib

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
conn_str = (
    r'Driver={{ODBC Driver 17 for SQL Server}};'
    r'Server={};'
    r'Database={};'
    r'Uid={};'
    r'Pwd={};'
    r'Encrypt=yes;'
    r'TrustServerCertificate=no;'
    r'Connection Timeout=30;'
)


class Config:
    JSON_SORT_KEYS = False
    SECRET_KEY = os.getenv("JWT_SECRET")
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote(os.getenv('AZURE_CONNECT_STRING'))


class DevelopmentConfig(Config):
    DEBUG = True
    conn_str = 'Driver={ODBC Driver 17 for SQL Server};' \
               'Server=127.0.0.1,43111;' \
               'uid=SA;' \
               'pwd=Password12$;' \
               'Database=hashtopdbDEV'
    url = urllib.parse.quote(conn_str)
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=' + url


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    conn_str = 'Driver={ODBC Driver 17 for SQL Server};' \
               'Server=127.0.0.1,43111;' \
               'uid=SA;' \
               'pwd=Password12$;' \
               'Database=hashtopdbTEST'
    url = urllib.parse.quote(conn_str)
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=' + url
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    DEBUG = True
    conn_str = conn_str.format(os.getenv('AZURE_SERVER'),
                               os.getenv('PROD_DB_NAME'),
                               os.getenv('AZURE_UID'),
                               os.getenv('AZURE_PWD')
                               )
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote(conn_str)


config_by_name = dict(
    DEV=DevelopmentConfig,
    TEST=TestingConfig,
    PROD=ProductionConfig
)

key = Config.SECRET_KEY

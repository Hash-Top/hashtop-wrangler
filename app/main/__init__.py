import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from .util import bcolors

bcrypt = Bcrypt()

from .config import config_by_name
env_name = os.getenv('ENVIRONMENT') or 'dev'
config_env = config_by_name[env_name]

if env_name == "prod":
    print(f"{bcolors.FAIL}{bcolors.BOLD}***** WARNING *****\n***** USING PRODUCTION *****{bcolors.ENDC}")
else:
    print(f"{bcolors.WARNING}USING ENVIRONMENT: {env_name}{bcolors.ENDC}")


from .model import Base
db = SQLAlchemy(metadata=Base.metadata)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_env)
    db.init_app(app)
    bcrypt.init_app(app)
    print("create app")
    return app
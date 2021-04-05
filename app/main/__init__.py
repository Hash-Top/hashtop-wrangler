from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

from .model import Base
from .config import config_by_name

db = SQLAlchemy(metadata=Base.metadata)
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    return app
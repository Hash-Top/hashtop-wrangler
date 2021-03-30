import uuid
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    wallet_addr = db.Column(db.String(42), primary_key=True)
    fname = db.Column(db.String)
    lname = db.Column(db.String)

    miners = db.relationship("Miner", back_populates="user", cascade="all, delete-orphan")
    stats = db.relationship("UserStat", back_populates="user", cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UserStat(db.Model):
    __tablename__ = "userStat"

    time = db.Column(db.DateTime, default=datetime.now(), primary_key=True)
    wallet_addr = db.Column(db.String(42), db.ForeignKey("user.wallet_addr", ondelete="CASCADE"), primary_key=True)
    user = db.relationship("User", back_populates="stats")

    balance = db.Column(db.Float)
    est_revenue = db.Column(db.Float)
    valid_shares = db.Column(db.Integer)
    stale_shares = db.Column(db.Integer)
    invalid_shares = db.Column(db.Integer)
    round_share_percent = db.Column(db.Float)
    effective_hashrate = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Miner(db.Model):
    __tablename__ = "miner"

    id = db.Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4())
    wallet_addr = db.Column(db.String(42), db.ForeignKey("user.wallet_addr", ondelete="CASCADE"))
    user = db.relationship("User", back_populates="miners")

    gpus = db.relationship("Gpu", back_populates="miner", cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Gpu(db.Model):
    __tablename__ = "gpu"

    miner_id = db.Column(UNIQUEIDENTIFIER, db.ForeignKey("miner.id", ondelete="CASCADE"), primary_key=True)
    gpu_no = db.Column(db.Integer, primary_key=True)
    miner = db.relationship("Miner", back_populates="gpus")

    healths = db.relationship("Health", cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Health(db.Model):
    __tablename__ = "health"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["miner_id", "gpu_no"], ["gpu.miner_id", "gpu.gpu_no"],
            ondelete="CASCADE"
        ),
    )

    # don't need backpopulates because we only ever insert into this table
    miner_id = db.Column(UNIQUEIDENTIFIER, primary_key=True)
    gpu_no = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, default=datetime.now(), primary_key=True)

    temperature = db.Column(db.Integer)
    power = db.Column(db.Integer)
    hashrate = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

#db.create_all()
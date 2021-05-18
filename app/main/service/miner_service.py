from datetime import datetime
from flask import Response
from app.main import db
from app.main.model.miner import Miner
from app.main.model.user import User
from .user_service import get_user
from . import logger, update, delete, save_changes
from sqlalchemy import exc

from ..model import Gpu, Health


def create_new_miner(data):
    user = get_user(data.get('user_id'))
    miner = db.session.query(Miner).filter_by(name=data.get('miner_name'),
                                              user=user)

    if not miner:
        new_miner = Miner(
            name=data.get('miner_name'),
            user_id=data.get('user_id'),
        )
        save_changes(new_miner)
        response_object = {
            'status': 'success',
            'message': 'Successfully added new miner.'
        }
        return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'Miner name already exists.',
        }
        return response_object, 409


def get_all_miners(user):
    return db.session.query(Miner).filter_by(user=user).all()


def get_miner(miner_id):
    return db.session.query(Miner).filter_by(id=miner_id).first()


#TODO: don't know if we need this as the dashboard will have access to the miners id
# when displayed in a list
def get_miner_by_name(user, miner_name):
    return db.session(Miner).filter_by(user=user, name=miner_name)


def get_stats_by_miner(miner, start, end):
    # get all health stats for all gpus in the miner
    gpu_health_stats = db.session.query(Health)\
        .join(Health.gpu)\
        .filter(Health.gpu.miner == miner)

    if start:
        gpu_health_stats = gpu_health_stats.filter(Gpu.healths.time >= start)
    if end:
        gpu_health_stats = gpu_health_stats.filter(Gpu.healths.time <= end)

    return gpu_health_stats

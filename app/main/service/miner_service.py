from sqlalchemy import select

from app.main import db
from . import logger, update, delete, save_changes

from ..model import Gpu, Health
from ..model.share import Share
from ..model.miner import Miner


def create_new_miner(data, user):
    miner = db.session.query(Miner).filter_by(name=data.get('miner_name'),
                                              user=user).first()
    if not miner:
        new_miner = Miner(
            name=data.get('miner_name'),
            user_id=user.id,
        )
        save_error = save_changes(new_miner)
        if save_error:
            return save_error
        else:
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


# TODO: don't know if we need this as the dashboard will have access to the miners id
# when displayed in a list
def get_miner_by_name(user, miner_name):
    return db.session(Miner).filter_by(user=user, name=miner_name)


def get_healths_by_miner(miner, start, end):
    # get all health stats for all gpus in the miner
    gpu_health_stats = db.session.query(Health) \
        .join(Gpu) \
        .filter(Gpu.miner == miner)

    if start:
        gpu_health_stats = gpu_health_stats.filter(Gpu.healths.time >= start)
    if end:
        gpu_health_stats = gpu_health_stats.filter(Gpu.healths.time <= end)

    stats = []
    # more efficient than querying using .all() so python doesn't load everything at once
    for s in gpu_health_stats.yield_per(100).limit(1000000):
        stats.append(s)

    return stats


def get_shares_by_miner(miner, start, end):
    # get all share stats for all gpus in the miner
    share_table = db.metadata.tables['share']
    gpu_table = db.metadata.tables['gpu']
    gpu_share_stats = select(share_table).select_from(
        share_table.join(gpu_table)).where(share_table.c.miner_id == miner.id)

    if start:
        gpu_share_stats = gpu_share_stats.where(share_table.time >= start)
    if end:
        gpu_share_stats = gpu_share_stats.where(share_table.time <= end)

    logger.debug(gpu_share_stats)
    result = db.engine.connect().execute(gpu_share_stats)

    shares = []
    # more efficient than querying using .all() so python doesn't load everything at once
    for s in result.yield_per(100):
        d = dict(s)
        # replace the enum with its string
        d['type'] = s.type.name
        shares.append(d)

    logger.debug(result)

    return shares

import itertools
from datetime import datetime, timedelta
from sqlalchemy import select

from app.main import db
from . import logger, update, delete, save_changes
from ..config import DEBUG
from ..model import Gpu, Health
from ..model.share import Share, ShareType
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


def get_shares_by_miner(miner, start, end, resolution):
    # not using default because it only affects empty function calls
    start = start or (datetime.utcnow() - timedelta(hours=12))
    end = end or datetime.utcnow()
    resolution = resolution or 5
    # get all share stats for all gpus in the miner
    timeframe_query = db.session.query(Share) \
        .filter(Share.miner_id == miner.id) \
        .filter(Share.time >= start) \
        .filter(Share.time <= end) \
        .order_by(Share.time)
    logger.debug(f"start time: {start} - end time: {end}")
    logger.debug(timeframe_query)

    min_query = db.session.query(Share) \
        .filter(Share.miner_id == miner.id) \
        .order_by(Share.time)\
        .limit(50000)

    query = timeframe_query if timeframe_query.count() > min_query.count() else min_query

    return aggregate(query, 5, "gpu_no", type="count")


def round_minutes(dt, resolution):
    new_minute = (dt.minute // resolution) * resolution
    return (dt + timedelta(minutes=new_minute - dt.minute)).replace(second=0, microsecond=0)


def aggregate(query, resolution, *groups, **aggregates):
    logger.debug(query)

    agg = {}
    window_size = 5000  # or whatever limit you like
    window_idx = 0
    while True:
        start, stop = window_size * window_idx, window_size * (window_idx + 1)
        rows = query.slice(start, stop).all()
        if rows is None:
            break
        for row in rows:
            interval_time = round_minutes(row.time, resolution)
            # key the aggregate based on the groups given
            key_list = [getattr(row, x) for x in groups]
            # apparently using insert is the fastest way to do this
            key_list.insert(0, interval_time)
            key = tuple(key_list)

            if key not in agg:
                # build a dict from the list of groups and aggregate cols
                agg[key] = {
                    'start': interval_time,
                    'duration': resolution,
                    # splice in the groups given so that each dict val can be flattened into a JSON array
                    **{group: getattr(row, group) for group in groups},
                    # handle "normal" aggregate cases
                    **{attr: getattr(row, attr) for (attr, agg_type) in aggregates.items() if agg_type != "count"},
                    # counts are handled by counting the number of distinct values that the attribute can take on
                    **{str(getattr(row, attr)): 0 for (attr, agg_type) in aggregates.items() if agg_type == "count"}
                }
            if DEBUG:
                print(agg[key])
            for attribute, aggregate_type in aggregates.items():
                # handle count case first, little bit ugly
                if aggregate_type == "count":
                    count_field = str(getattr(row, attribute))
                    # if the key doesnt include the aggregate we need to create an entry for it in the dict
                    agg[key].setdefault(count_field, 0)
                    # finally we can increment the count
                    agg[key][count_field] += 1
                else:
                    aggregate_val = agg[key][attribute]
                    if aggregate_type == 'max':
                        agg[key][attribute] = max(getattr(row, attribute), aggregate_val)
                    elif aggregate_type == "min":
                        agg[key][attribute] = min(getattr(row, attribute), aggregate_val)
                    elif aggregate_type == "sum":
                        agg[key][attribute] += getattr(row, attribute)

        if len(rows) < window_size:
            break
        window_idx += 1
    if DEBUG:
        for item in agg.values():
            print(item)
    logger.debug(next(iter(agg.values()), None))
    return list(agg.values())

import itertools
from datetime import datetime, timedelta
from sqlalchemy import select

from app.main import db
from . import logger, update, delete, save_changes
from ..config import DEBUG
from ..model import Gpu, Health
from ..model.share import Share, ShareType
from ..model.miner import Miner


def create_new_miner(data):
    miner = db.session.query(Miner).filter_by(name=data.get('id')).first()
    if not miner:
        new_miner = Miner(
            id=data.get('id'),
            name=data.get('name'),
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


def get_healths_by_miner(miner, start, end, resolution):
    # not using default because it only affects empty function calls
    start = start or (datetime.utcnow() - timedelta(hours=12))
    end = end or datetime.utcnow()
    resolution = resolution or 1
    # get all health stats for all gpus in the miner
    timeframe_query = db.session.query(Health) \
        .filter(Health.miner_id == miner.id) \
        .filter(Health.time >= start) \
        .filter(Health.time <= end) \
        .order_by(Health.time)
    logger.debug(f"start time: {start} - end time: {end}")
    logger.debug(timeframe_query)

    return aggregate(timeframe_query, resolution,
                     "gpu_no",
                     "gpu_name",
                     fan_speed="avg",
                     temperature="avg",
                     power_draw="avg",
                     power_limit="avg",
                     hashrate="avg",
                     core_clock="avg",
                     mem_clock="avg")


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

    return aggregate(timeframe_query, resolution, "gpu_no", type="count")


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
                    **{attr: getattr(row, attr) for (attr, agg_type) in aggregates.items()
                       if agg_type != "count" and agg_type != "avg"},
                    # counts are handled by counting the number of distinct values that the attribute can take on
                    **{str(getattr(row, attr)): 0 for (attr, agg_type) in aggregates.items() if agg_type == "count"}
                }
            for attribute, aggregate_type in aggregates.items():
                # handle count case first, little bit ugly
                if aggregate_type == "count":
                    count_field = str(getattr(row, attribute))
                    # if the key doesnt include the aggregate we need to create an entry for it in the dict
                    agg[key].setdefault(count_field, 0)
                    # finally we can increment the count
                    agg[key][count_field] += 1
                else:
                    aggregate_val = agg[key].get(attribute)
                    if aggregate_type == "max":
                        agg[key][attribute] = max(getattr(row, attribute), aggregate_val)
                    elif aggregate_type == "min":
                        agg[key][attribute] = min(getattr(row, attribute), aggregate_val)
                        agg[key][attribute] += getattr(row, attribute)
                    elif aggregate_type == "avg":
                        # to calculate the avg all of the values must be stored
                        val = getattr(row, attribute)
                        if not val:
                            val = 0
                        agg[key].setdefault(attribute, []).append(val)

        if len(rows) < window_size:
            break
        window_idx += 1

    # go through and calculate the avg for any aggregates
    for a in agg.values():
        for attribute, aggregate_type in aggregates.items():
            if aggregate_type == "avg":
                # find the avg of the list stored for the avg aggregate
                a[attribute] = sum(a[attribute]) / len(a[attribute])

    if DEBUG:
        item = next(iter(agg.values()), None)
        print(item)
        logger.debug(item)

    return list(agg.values())

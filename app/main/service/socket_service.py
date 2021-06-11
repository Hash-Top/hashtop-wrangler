import os
from datetime import datetime

from app.main import db
from app.main.model.miner import Miner
from app.main.model.share import Share, ShareType
from .miner_service import get_miner
from . import logger, update, delete, save_changes
from .slack_notify_service import notify_slack
from ..model import Gpu, Health


def update_shares(miner_uuid, data):
    miner = get_miner(miner_uuid)

    if miner:
        gpu_no = data.get('gpu_no')
        share_type = data.get('share_type')
        ts = int(data.get('timestamp'))
        gpu = get_gpu(miner, gpu_no)
        if gpu:
            # create a new share object in the db from the websocket payload
            new_share = Share(
                miner_id=miner_uuid,
                gpu_no=gpu_no,
                type=ShareType[share_type],
                time=datetime.fromtimestamp(ts)
            )
            # notify slack of invalid shares
            if share_type == 'invalid':
                notify_slack(new_share)

            save_changes(new_share)
            response_object = {
                'status': 'success',
                'message': f'Successfully added new {share_type} share data for gpu {gpu_no}.'
            }
            response_payload = response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': f'GPU {gpu_no} doesn\'t exist in this miner.',
            }
            response_payload = response_object, 409

    else:
        response_object = {
            'status': 'fail',
            'message': f'No miner matching the UUID {miner_uuid}.',
        }

        response_payload = response_object, 409

    if os.getenv('DEBUG').upper() == 'TRUE':
        print(response_payload)
    return response_payload


def update_healths(miner_uuid, data):
    miner = get_miner(miner_uuid)

    if miner:
        ts = int(data.get('timestamp'))
        gpu_no = data.get('gpu_no')
        gpu_name = data.get('gpu_name')
        fan_speed = data.get('fan_speed')
        temperature = data.get('temperature')
        power_draw = data.get('power_draw')
        power_limit = data.get('power_limit')
        gpu = get_gpu(miner, gpu_no)

        if gpu:
            # create a new share object in the db from the websocket payload
            new_health = Health(
                time=datetime.fromtimestamp(ts),
                miner_id=miner_uuid,
                gpu_no=gpu_no,
                gpu_name=gpu_name,
                fan_speed=fan_speed,
                temperature=temperature,
                power_draw=power_draw,
                power_limit=power_limit
            )

            save_changes(new_health)
            response_object = {
                'status': 'success',
                'message': f'Successfully added new health data for gpu {gpu_no}.'
            }
            response_payload = response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': f'GPU {gpu_no} doesn\'t exist in this miner.',
            }
            response_payload = response_object, 409

    else:
        response_object = {
            'status': 'fail',
            'message': f'No miner matching the UUID {miner_uuid}.',
        }

        response_payload = response_object, 409

    if os.getenv('DEBUG').upper() == 'TRUE':
        print(response_payload)
    return response_payload


def get_gpu(miner, gpu_no):
    return db.session.query(Gpu).filter_by(gpu_no=gpu_no, miner_id=miner.id).first()

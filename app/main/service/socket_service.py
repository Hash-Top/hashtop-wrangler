from datetime import datetime

from app.main import db
from app.main.model.miner import Miner
from app.main.model.gpu import Share, ShareType
from .miner_service import get_miner
from . import logger, update, delete, save_changes
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
            save_changes(new_share)
            response_object = {
                'status': 'success',
                'message': f'Successfully added new {share_type} share data for gpu {gpu_no}.'
            }
            return response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': f'GPU {gpu_no} doesn\'t exist in this miner.',
            }
            return response_object, 409

    else:
        response_object = {
            'status': 'fail',
            'message': f'No miner matching the UUID {miner_uuid}.',
        }
        return response_object, 409


def get_gpu(miner, gpu_no):
    return db.session.query(Gpu).filter_by(gpu_no=gpu_no, miner_id=miner.id).first()

from flask_socketio import Namespace, emit
from app.main import socketio
from ..service.socket_service import update_shares, update_healths
from app.main.base_logger import logger

logger = logger.getLogger(__name__)


class MinerSocket(Namespace):
    def on_connect(self):
        logger.info('connected')
        emit('success', {'data': 'Connected'})

    def on_disconnect(self):
        logger.info('Client disconnected')

    def on_share_update(self, miner_uuid, data):
        logger.debug('received args: ' + ', '.join([miner_uuid, str(data)]))
        emit(update_shares(miner_uuid, data))

    def on_health_update(self, miner_uuid, data):
        logger.debug('received args: ' + ', '.join([miner_uuid, str(data)]))
        responses = []
        for health in data:
            responses.append(update_healths(miner_uuid, health))
        emit(responses)


socketio.on_namespace(MinerSocket('/'))

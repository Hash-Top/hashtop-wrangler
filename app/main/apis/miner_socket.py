from flask_socketio import Namespace, emit
from app.main import socketio
from ..service.socket_service import update_shares, update_healths


class MinerSocket(Namespace):
    def on_connect(self):
        print("connected")
        emit('success', {'data': 'Connected'})

    def on_disconnect(self):
        print('Client disconnected')

    def on_share_update(self, miner_uuid, data):
        print("received args: " + ", ".join([miner_uuid, str(data)]))
        return update_shares(miner_uuid, data)

    def on_health_update(self, miner_uuid, data):
        print("received args: " + ", ".join([miner_uuid, str(data)]))
        return update_healths(miner_uuid, data)


socketio.on_namespace(MinerSocket('/'))

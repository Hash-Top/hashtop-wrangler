from flask_socketio import emit
from app.main import socketio
from ..service.socket_service import update_shares

@socketio.on('health_update')
def handle_health_update(miner_uuid, data):
    print("received args: " + ", ".join([miner_uuid, str(data)]))
    return update_shares(miner_uuid, data)


@socketio.on('connect')
def test_connect():
    print("connected")
    emit('success', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
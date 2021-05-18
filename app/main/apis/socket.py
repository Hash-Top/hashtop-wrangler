from flask_socketio import emit
from app.main import socketio


@socketio.on('health_update')
def handle_health_update(miner_uuid, data):
    print("received args: " + ", ".join([miner_uuid, str(data)]))
    


@socketio.on('connect')
def test_connect():
    print("connected")
    emit('success', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')



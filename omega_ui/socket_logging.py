import eventlet
import flask
import flask_socketio as fsio
import json
import redis

import omega_ui.configuration as oc

eventlet.monkey_patch()
pool = eventlet.GreenPool(1000)  # number of available connections
async_mode = 'eventlet'

s_app = flask.Flask(__name__)
s_app.config['SECRET_KEY'] = 'secret!'
socketio = fsio.SocketIO(s_app, async_mode=None)


def background_thread(uid_with_size):
    uid, size = uid_with_size.split(';')
    r = redis.StrictRedis(oc.cfg['default']['redis'], 6379, db=0)
    r.set(uid+'size', size)
    pubsub = r.pubsub()
    pubsub.subscribe('l'+uid)
    count = 0
    for message in pubsub.listen():
        # Filter out events like Redis connections.
        if message['type'] != 'message':
            continue
        count += 1
        socketio.sleep(0.01)
        try:
            data = json.loads(message['data'].decode('utf8'))
            msg = uid + data['name'] + ': ' + data['levelname'] + ': ' + data['msg']
            socketio.emit('log_response', {'data': msg, 'count': count}, namespace='/omega_log')
        except:
            pass


@socketio.on('connect_event', namespace='/omega_log')
def test_message(message):
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    pool.spawn(background_thread, message['data'])
    fsio.emit('log_response', {'data': message['data'], 'count': flask.session['receive_count']})


@socketio.on('connect', namespace='/omega_log')
def connect():
    print('Client connected', flask.request.sid)
    fsio.emit('log_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/omega_log')
def disconnect():
    print('Client disconnected', flask.request.sid)


if __name__ == '__main__':
    socketio.run(s_app, host='0.0.0.0', debug=True)

# backend/wsgi.py

from app import app, socketio

# Wrap the Flask app with SocketIO's WSGI middleware
application = socketio.WSGIApp(socketio, app)

if __name__ == "__main__":
    socketio.run(app)

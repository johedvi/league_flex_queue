# backend/wsgi.py

from app import app, socketio

# Expose the SocketIO server as the WSGI application
application = socketio

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)

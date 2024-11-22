# backend/wsgi.py

from app import socketio

# Expose the SocketIO instance as the WSGI application
application = socketio

if __name__ == "__main__":
    socketio.run(application)

# backend/wsgi.py

from app import app

# Expose the Flask app as the WSGI application
application = app
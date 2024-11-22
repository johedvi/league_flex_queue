
API_KEY = 'RGAPI-ad0f9df6-5fb9-4c3d-aa86-0bdaf58b23b6'
DEFAULT_REGION_CODE = 'eune1'
DEFAULT_REGION = 'europe'
BACKEND_URL = 'https://blackultrasflex-backend.onrender.com'
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = "RGAPI-ad0f9df6-5fb9-4c3d-aa86-0bdaf58b23b6"
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///players.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKEND_URL = 'https://blackultrasflex-backend.onrender.com'


API_KEY = "RGAPI-c592ffbb-a523-4f4b-b2c4-c40ba5fa7040"
DEFAULT_REGION_CODE = 'eune1'
DEFAULT_REGION ='europe'


# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    API_KEY = "RGAPI-c592ffbb-a523-4f4b-b2c4-c40ba5fa7040"
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///players.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = 'RGAPI-4597da49-697c-475f-b75d-97983cb2b904' #os.environ.get('API_KEY')
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKEND_URL = 'api.blackultras.com'


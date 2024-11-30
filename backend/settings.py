# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = os.environ.get('API_KEY')
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI =  'postgresql://blackultrasdb_8b23_user:AFRcep5dbUvMKeZSkZGy57RT3Nci6Lr3@dpg-ct5mkhi3esus73f8hso0-a.frankfurt-postgres.render.com/blackultrasdb_8b23'#os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKEND_URL = 'api.blackultras.com'


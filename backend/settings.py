# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = os.environ.get('API_KEY')
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI =  'postgresql://blackultrasdb_user:W5NhDEgrkKjtdQJUPeFbGyXq8xXvmtg9@dpg-ct5mas3tq21c7399psi0-a.frankfurt-postgres.render.com/blackultrasdb'#os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKEND_URL = 'api.blackultras.com'


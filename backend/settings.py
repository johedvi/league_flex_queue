# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = os.environ.get('API_KEY')
    DEFAULT_REGION_CODE = 'eune1'
    DEFAULT_REGION = 'europe'    
    SQLALCHEMY_DATABASE_URI = 'postgresql://blackultras_user:jQPWjQM6YsBgjyArqRGyhhAOgYWTSott@dpg-ct0ah3e8ii6s73fjvha0-a.frankfurt-postgres.render.com/blackultras'#os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKEND_URL = 'api.blackultras.com'


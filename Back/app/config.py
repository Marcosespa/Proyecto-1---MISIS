import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    PROJECT_ID = os.getenv('PROJECT_ID')
    PROCESSING_TOPIC = os.getenv('PROCESSING_TOPIC')
    COMPLETION_TOPIC = os.getenv('COMPLETION_TOPIC')
    ERROR_TOPIC = os.getenv('ERROR_TOPIC')

config = Config()

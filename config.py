import os
import json

from dotenv import load_dotenv

load_dotenv()
app_dir = os.path.abspath(os.path.dirname(__file__))

TRANSMISSION_HOST = 'localhost'
TRANSMISSION_PORT = 9091
TRANSMISSION_USER = 'vova'
TRANSMISSION_PASSWORD = 'vova12345'

with open('jackett_data/Jackett/ServerConfig.json') as jackett_file:
    api_key = json.load(jackett_file).get('APIKey')

JACKETT_API_KEY = api_key


class DevelopmentConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

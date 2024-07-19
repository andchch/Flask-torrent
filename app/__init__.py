import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(
    os.environ.get('FLASK_ENV') or 'config.DevelopmentConfig'
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs('app/files', exist_ok=True)

from . import views

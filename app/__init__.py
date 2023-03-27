import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Übernommen aus den Beispielen von Miguel Grinberg
# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

## Initialize LoginManager
login = LoginManager(app)
login.login_view = 'login'
login.login_message = ('Please log in to access this page.')

# Übernommen aus den Beispielen von Miguel Grinberg
from app import routes, models, errors
from app.api import users, tokens, errors

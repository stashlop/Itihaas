"""Flask extension instances.

Extensions are created here, unbound, and initialised inside
:func:`itihaas.create_app`. Keeping them in their own module avoids circular
imports between the application factory, models and blueprints.
"""
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from flask_login import LoginManager, current_user
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Load environment variables from .env for development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from website.translations import translations
from website.chatbot import chatbot_bp
from flask_mail import Mail
from .email_utils import mail
from flask_babel import Babel
import config  # Changed from relative import

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"

# Load spaCy English model
nlp = None


def create_app(config_class=config.Config):  # Updated to use config.Config
    app = Flask(__name__)
    global nlp
    # Attempt to load spaCy model lazily; proceed if not present
    if nlp is None:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"spaCy model not available: {e}. Continuing without NLP features.")
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    # Add Google Maps API key configuration
    app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    if not app.config['GOOGLE_MAPS_API_KEY']:
        print("WARNING: Google Maps API key not set! Please set GOOGLE_MAPS_API_KEY environment variable.")
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail settings
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    if not email_user or not email_password:
        print("WARNING: Email credentials not set! Please set EMAIL_USER and EMAIL_PASSWORD environment variables.")
        print(f"Current EMAIL_USER: {'Set' if email_user else 'Not Set'}")
        print(f"Current EMAIL_PASSWORD: {'Set' if email_password else 'Not Set'}")
    
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=email_user,
        MAIL_PASSWORD=email_password,
        MAIL_DEFAULT_SENDER=email_user,
        MAIL_MAX_EMAILS=None,
        MAIL_ASCII_ATTACHMENTS=False,
        MAIL_DEBUG=True,
        MAIL_SUPPRESS_SEND=False
    )

    try:
        mail.init_app(app)
        with app.app_context():
            # Test email configuration
            mail.connect()
            print("Email configuration successful!")
            print(f"Using email: {email_user}")
            print("Make sure you have:")
            print("1. Enabled 2-Step Verification in your Google Account")
            print("2. Generated an App Password for this application")
            print("3. Used the App Password (not your regular Gmail password)")
    except Exception as e:
        print(f"Error initializing email: {str(e)}")
        print("Common issues:")
        print("1. Gmail 2-Step Verification not enabled")
        print("2. Using regular password instead of App Password")
        print("3. Incorrect App Password format")
        print("4. Gmail account security settings blocking access")

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth
    from .merchandise import merchandise_bp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(merchandise_bp)

    from .models import User, Note, Site, Category, Region, IsoCode, Booking, Guide, GuideDetails, Transaction, TourPackage, Review
    from .merchandise_models import Merchandise, CartItem, Order, OrderItem
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Translation helper
    @app.context_processor
    def utility_processor():
        def _(key):
            lang = session.get('lang', 'en')
            return translations[lang].get(key, translations['en'].get(key, key))
        return dict(_=_)

    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    # Language switcher route
    @app.route('/change-language', methods=['POST'])
    def change_language():
        from flask import request, jsonify
        data = request.get_json()
        lang = data.get('lang')
        if lang in translations:
            session['lang'] = lang
        return jsonify({'status': 'success'})

    with app.app_context():
        db.create_all()

    return app


def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
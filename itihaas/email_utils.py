from flask_mail import Mail, Message
from flask import current_app
import logging
import os

mail = Mail()

def setup_email_logging():
    logger = logging.getLogger('email_utils')
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('email.log')
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    
    # Create formatters and add it to handlers
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    c_format = logging.Formatter(format_str)
    f_format = logging.Formatter(format_str)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger

logger = setup_email_logging()

def send_verification_email(user_email, verification_code):
    try:
        # Check if email configuration is set
        if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
            logger.error('Email configuration is missing. Please set EMAIL_USER and EMAIL_PASSWORD environment variables.')
            return False

        msg = Message(
            'Verify your Itihaas account',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user_email]
        )
        msg.html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #f1683a;">Welcome to Itihaas!</h2>
            <p>Thank you for signing up. To complete your registration, please use the following verification code:</p>
            <div style="background-color: #f8f8f8; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="color: #f1683a; letter-spacing: 5px; margin: 0;">{verification_code}</h1>
            </div>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
            <p>Best regards,<br>The Itihaas Team</p>
        </div>
        '''
        
        logger.info(f'Attempting to send verification email to {user_email}')
        mail.send(msg)
        logger.info(f'Successfully sent verification email to {user_email}')
        return True
        
    except Exception as e:
        logger.error(f'Error sending email to {user_email}: {str(e)}')
        # Log detailed configuration for debugging
        logger.debug(f'Mail Server: {current_app.config.get("MAIL_SERVER")}')
        logger.debug(f'Mail Port: {current_app.config.get("MAIL_PORT")}')
        logger.debug(f'Mail Use TLS: {current_app.config.get("MAIL_USE_TLS")}')
        logger.debug(f'Mail Username: {current_app.config.get("MAIL_USERNAME")}')
        logger.debug(f'Mail Default Sender: {current_app.config.get("MAIL_DEFAULT_SENDER")}')
        return False 
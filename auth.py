from flask import Blueprint, Flask, render_template, request, flash, redirect, url_for, session, jsonify
from .models import User, Guide, ItihaasCoins, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .email_utils import send_verification_email


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Special case for admin user
        if email == 'itihaasdairy@gmail.com' and password == '12345678':
            # Create or get admin user
            admin_user = User.query.filter_by(email=email).first()
            if not admin_user:
                admin_user = User(
                    email=email,
                    first_name='itihaas',
                    password=generate_password_hash(password),
                    is_verified=True
                )
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user, remember=True)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.admin_dashboard'))

        # Regular user login
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                if not user.is_verified:
                    flash('Please verify your email first.', category='error')
                    return redirect(url_for('auth.verify_email'))
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1),
                is_verified=False
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Generate and send verification code
            verification_code = new_user.generate_verification_code()
            db.session.commit()
            
            if send_verification_email(email, verification_code):
                session['email_for_verification'] = email
                flash('Please check your email for verification code.', category='success')
                return redirect(url_for('auth.verify_email'))
            else:
                flash('Error sending verification email. Please try again.', category='error')
                db.session.delete(new_user)
                db.session.commit()

    return render_template("sign_up.html", user=current_user)


@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'email_for_verification' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        user = User.query.filter_by(email=session['email_for_verification']).first()
        
        if not user:
            flash('User not found.', category='error')
            return redirect(url_for('auth.login'))
        
        if user.verify_code(verification_code):
            db.session.commit()
            session.pop('email_for_verification', None)
            flash('Email verified successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid or expired verification code.', category='error')
    
    return render_template('verify_email.html', user=current_user)


@auth.route('/resend-verification')
def resend_verification():
    if 'email_for_verification' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=session['email_for_verification']).first()
    if not user:
        flash('User not found.', category='error')
        return redirect(url_for('auth.login'))
    
    verification_code = user.generate_verification_code()
    db.session.commit()
    
    if send_verification_email(user.email, verification_code):
        flash('Verification code resent. Please check your email.', category='success')
    else:
        flash('Error sending verification email. Please try again.', category='error')
    
    return redirect(url_for('auth.verify_email'))


@auth.route('/guide-signup', methods=['GET', 'POST'])
def guide_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        phone = request.form.get('phone')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            try:
                # Create new user with is_guide=True and is_verified=False
                new_user = User(
                    email=email,
                    first_name=first_name,
                    password=generate_password_hash(password1),
                    is_guide=True,
                    is_verified=False
                )
                db.session.add(new_user)
                db.session.flush()

                # Create guide profile with basic info
                guide = Guide(
                    user_id=new_user.id,
                    name=first_name,
                    phone=phone
                )
                db.session.add(guide)
                
                # Generate and send verification code
                verification_code = new_user.generate_verification_code()
                db.session.commit()
                
                if send_verification_email(email, verification_code):
                    session['email_for_verification'] = email
                    flash('Please check your email for verification code.', category='success')
                    return redirect(url_for('auth.verify_email'))
                else:
                    flash('Error sending verification email. Please try again.', category='error')
                    db.session.delete(new_user)
                    db.session.commit()

            except Exception as e:
                db.session.rollback()
                flash('An error occurred while creating your account.', category='error')
                print(e)

    return render_template("guide_signup.html", user=current_user)


@auth.route('/update-coins', methods=['POST'])
@login_required
def update_coins():
    try:
        data = request.get_json()
        reward_coins = data.get('reward_coins', 0)
        used_coins = data.get('used_coins', 0)
        transaction_id = data.get('transaction_id')

        # Get or create ItihaasCoins record for the user
        itihaas_coins = ItihaasCoins.query.filter_by(user_id=current_user.id).first()
        if not itihaas_coins:
            itihaas_coins = ItihaasCoins(user_id=current_user.id, coins=0)
            db.session.add(itihaas_coins)

        # Update coins balance
        current_balance = itihaas_coins.coins
        new_balance = current_balance + reward_coins - used_coins
        itihaas_coins.coins = new_balance

        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            amount=reward_coins,
            transaction_type='reward' if reward_coins > 0 else 'payment',
            transaction_id=transaction_id
        )
        db.session.add(transaction)

        # Commit changes
        db.session.commit()

        return jsonify({
            'success': True,
            'new_balance': new_balance
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


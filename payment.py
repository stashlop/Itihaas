from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import stripe
import os
from datetime import datetime
from .models import db, Booking, Payment

# Initialize Stripe with your secret key
stripe.api_key = 'your_stripe_secret_key'  # Replace with your actual Stripe secret key

# Create Blueprint
payment = Blueprint('payment', __name__)

@payment.route('/checkout/<int:booking_id>', methods=['GET'])
@login_required
def checkout(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Get the amount from the booking
        amount = booking.total_amount
        
        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': int(amount * 100),  # Convert to paise
                    'product_data': {
                        'name': f'Booking for {booking.monument_name}',
                        'description': f'Date: {booking.visit_date}, Visitors: {booking.visitors}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment.success', booking_id=booking.id, _external=True),
            cancel_url=url_for('payment.cancel', booking_id=booking.id, _external=True),
            customer_email=current_user.email,
        )
        
        return render_template('payment/checkout.html', 
                             checkout_session_id=checkout_session.id,
                             booking=booking,
                             stripe_public_key='your_stripe_public_key')  # Replace with your Stripe public key
    
    except Exception as e:
        flash('An error occurred during checkout. Please try again.', 'error')
        return redirect(url_for('views.bookings'))

@payment.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'your_webhook_secret'  # Replace with your webhook secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Handle successful payment
        handle_successful_payment(session)
    
    return jsonify({'status': 'success'})

def handle_successful_payment(session):
    # Extract booking_id from metadata or success_url
    booking_id = extract_booking_id_from_session(session)
    
    if booking_id:
        booking = Booking.query.get(booking_id)
        if booking:
            # Create payment record
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=session.amount_total / 100,  # Convert from paise to rupees
                payment_id=session.payment_intent,
                status='completed',
                payment_date=datetime.utcnow()
            )
            
            # Update booking status
            booking.payment_status = 'paid'
            
            # Save to database
            db.session.add(payment)
            db.session.commit()

def extract_booking_id_from_session(session):
    # Extract booking_id from success_url
    success_url = session.get('success_url', '')
    try:
        # Assuming the success_url contains booking_id as a parameter
        booking_id = int(success_url.split('booking_id=')[1].split('&')[0])
        return booking_id
    except:
        return None

@payment.route('/success/<int:booking_id>')
@login_required
def success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('payment/success.html', booking=booking)

@payment.route('/cancel/<int:booking_id>')
@login_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('payment/cancel.html', booking=booking)

# API endpoint to create a payment intent
@payment.route('/create-payment-intent/<int:booking_id>', methods=['POST'])
@login_required
def create_payment_intent(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Get the amount from the booking
        amount = booking.total_amount
        
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to rupees to paise
            currency='inr',
            metadata={'booking_id': booking.id}
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@payment.route('/refund/<int:booking_id>', methods=['POST'])
@login_required
def refund_payment(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        payment = Payment.query.filter_by(booking_id=booking_id).first()
        
        if not payment:
            flash('No payment found for this booking.', 'error')
            return redirect(url_for('views.bookings'))
        
        # Create refund through Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.payment_id,
            amount=int(payment.amount * 100)  # Convert to paise
        )
        
        if refund.status == 'succeeded':
            # Update payment status
            payment.status = 'refunded'
            booking.payment_status = 'refunded'
            db.session.commit()
            
            flash('Refund processed successfully.', 'success')
        else:
            flash('Refund could not be processed.', 'error')
            
        return redirect(url_for('views.bookings'))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('views.bookings'))

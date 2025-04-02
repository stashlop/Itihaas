from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .models import Booking, Guide, ItihaasCoins, TourPackage, Review, User, Transaction
from .merchandise_models import Merchandise
from . import db
import random
import time
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app
from .whatsapp import send_booking_confirmation

views = Blueprint('views', __name__)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/about')
def about():
    return render_template("about.html", user=current_user)

@views.route('/vlog')
def vlog():
    return render_template("vlog.html", user=current_user)

@views.route('/review')
@login_required
def review():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('review.html', reviews=reviews)

@views.route('/api/reviews', methods=['POST'])
@login_required
def create_review():
    try:
        monument_name = request.form.get('monument_name')
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review_text')
        tags = json.loads(request.form.get('tags', '[]'))
        
        # Handle photo uploads
        photos = []
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    photos.append(url_for('static', filename=f'uploads/{filename}'))
        
        review = Review(
            user_id=current_user.id,
            monument_name=monument_name,
            rating=rating,
            review_text=review_text,
            tags=tags,
            photos=photos
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Return review data with user info
        review_data = {
            'id': review.id,
            'monument_name': review.monument_name,
            'rating': review.rating,
            'review_text': review.review_text,
            'tags': review.tags,
            'photos': review.photos,
            'created_at': review.created_at,
            'user': {
                'id': current_user.id,
                'first_name': current_user.first_name,
                'profile_pic': current_user.profile_pic
            }
        }
        
        return jsonify({'message': 'Review submitted successfully', 'review': review_data}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@views.route('/index')
@login_required
def place():
    festival_sites = {
        'january': {
            'festivals': ['Makar Sankranti', 'Pongal', 'Lohri', 'Bihu'],
            'sites': ['Great Living Chola Temples', 'Rani-ki-Vav']
        },
        'march': {
            'festivals': ['Holi', 'Maha Shivratri'],
            'sites': ['Khajuraho Group of Monuments', 'Ellora Caves', 'Mahabodhi Temple']
        },
        'august': {
            'festivals': ['Raksha Bandhan', 'Janmashtami', 'Ganesh Chaturthi'],
            'sites': ['Sun Temple Konark', 'Elephanta Caves', 'Jaipur City']
        },
        'october': {
            'festivals': ['Diwali', 'Chhath Puja'],
            'sites': ['Taj Mahal', 'Agra Fort', 'Fatehpur Sikri']
        },
        'december': {
            'festivals': ['Christmas', 'New Year'],
            'sites': ['Churches of Goa', 'Victorian Gothic Mumbai']
        }
    }
    return render_template("index.html", user=current_user, festival_sites=festival_sites)

@views.route('/map')
@login_required
def map_view():
    heritage_sites = [
        # Agra (Uttar Pradesh)
        {
            "name": "Taj Mahal",
            "description": "An ivory-white marble mausoleum, one of the world's most iconic monuments.",
            "lat": 27.1751,
            "lng": 78.0421
        },
        {
            "name": "Agra Fort",
            "description": "UNESCO World Heritage site, a historical fortress and palace complex.",
            "lat": 27.1797,
            "lng": 78.0216
        },
        {
            "name": "Fatehpur Sikri",
            "description": "Former capital of the Mughal Empire, known for its Persian and Mughal architecture.",
            "lat": 27.0940,
            "lng": 77.6711
        },
        {
            "name": "Itimad-ud-Daulah's Tomb",
            "description": "Known as the 'Baby Taj', this tomb is often regarded as a draft of the Taj Mahal.",
            "lat": 27.1927,
            "lng": 78.0307
        },
        {
            "name": "Akbar's Tomb",
            "description": "The tomb of the great Mughal emperor Akbar, located in Sikandra.",
            "lat": 27.2219,
            "lng": 77.9401
        },
        # Maharashtra
        {
            "name": "Chhatrapati Shivaji Terminus",
            "description": "Historic railway station and UNESCO World Heritage site in Mumbai.",
            "lat": 18.9398,
            "lng": 72.8355
        },
        {
            "name": "Gateway of India",
            "description": "Iconic arch monument built in the early 20th century in Mumbai.",
            "lat": 18.9220,
            "lng": 72.8347
        },
        {
            "name": "Ajanta Caves",
            "description": "Ancient Buddhist cave monuments dating from 2nd century BCE.",
            "lat": 20.5519,
            "lng": 75.7033
        },
        {
            "name": "Ellora Caves",
            "description": "Archaeological site with Hindu, Buddhist and Jain cave temples.",
            "lat": 20.0258,
            "lng": 75.1780
        },
        {
            "name": "Bibi-ka-Maqbara",
            "description": "Known as the 'Taj of the Deccan', architectural marvel in Aurangabad.",
            "lat": 19.9018,
            "lng": 75.3186
        },
        {
            "name": "Sindhudurg Fort",
            "description": "16th-century coastal fort built by Chhatrapati Shivaji Maharaj.",
            "lat": 16.0467,
            "lng": 73.4592
        },
        {
            "name": "Shaniwar Wada",
            "description": "Historical fortification in Pune, former seat of the Peshwa rulers.",
            "lat": 18.5195,
            "lng": 73.8553
        },
        {
            "name": "Pratapgad Fort",
            "description": "Mountain fort significant in Maratha history.",
            "lat": 17.9373,
            "lng": 73.5408
        },
        # Delhi
        {
            "name": "Lotus Temple",
            "description": "Remarkable architecture of the Baháʼí House of Worship.",
            "lat": 28.5535,
            "lng": 77.2588
        },
        {
            "name": "Red Fort",
            "description": "Historic fort complex built in the 17th century.",
            "lat": 28.6562,
            "lng": 77.2410
        },
        {
            "name": "India Gate",
            "description": "War memorial dedicated to soldiers of British Indian Army.",
            "lat": 28.6129,
            "lng": 77.2295
        },
        {
            "name": "Qutub Minar",
            "description": "UNESCO World Heritage site, tallest brick minaret in the world.",
            "lat": 28.5244,
            "lng": 77.1855
        },
        {
            "name": "Humayun's Tomb",
            "description": "1570 Mughal architecture that inspired the Taj Mahal.",
            "lat": 28.5933,
            "lng": 77.2507
        },
        {
            "name": "Jama Masjid",
            "description": "India's largest mosque, built by Mughal Emperor Shah Jahan.",
            "lat": 28.6507,
            "lng": 77.2334
        },
        # Goa
        {
            "name": "Basilica of Bom Jesus",
            "description": "UNESCO World Heritage site containing the remains of St. Francis Xavier.",
            "lat": 15.5009,
            "lng": 73.9116
        },
        {
            "name": "Chapora Fort",
            "description": "Ancient fort offering panoramic views of the Arabian Sea.",
            "lat": 15.6016,
            "lng": 73.7346
        },
        {
            "name": "Fort Aguada",
            "description": "17th-century Portuguese fort and lighthouse.",
            "lat": 15.4989,
            "lng": 73.7633
        },
        {
            "name": "Se Cathedral",
            "description": "Largest church in Asia, dedicated to St. Catherine.",
            "lat": 15.5034,
            "lng": 73.9147
        },
        # Kerala
        {
            "name": "Bekal Fort",
            "description": "Largest fort in Kerala, overlooking the Arabian Sea.",
            "lat": 12.3917,
            "lng": 75.0327
        },
        {
            "name": "Jewish Synagogue",
            "description": "Oldest active synagogue in the Commonwealth of Nations.",
            "lat": 9.9578,
            "lng": 76.2595
        },
        {
            "name": "Krishnapuram Palace",
            "description": "Rare example of Kerala's architectural style.",
            "lat": 9.1672,
            "lng": 76.4994
        },
        {
            "name": "Dutch Palace",
            "description": "Also known as Mattancherry Palace, featuring Kerala murals.",
            "lat": 9.9589,
            "lng": 76.2593
        },
        # Rajasthan
        {
            "name": "Hawa Mahal",
            "description": "Palace with unique honeycomb-like structure in Jaipur.",
            "lat": 26.9239,
            "lng": 75.8267
        },
        {
            "name": "City Palace Jaipur",
            "description": "Complex of courtyards, gardens and buildings in Jaipur.",
            "lat": 26.9258,
            "lng": 75.8237
        },
        {
            "name": "Chittorgarh Fort",
            "description": "Largest fort in India, UNESCO World Heritage site.",
            "lat": 24.8879,
            "lng": 74.6446
        },
        {
            "name": "Jantar Mantar",
            "description": "UNESCO World Heritage site, astronomical observation site.",
            "lat": 26.9247,
            "lng": 75.8243
        },
        # Punjab
        {
            "name": "Golden Temple",
            "description": "Holiest Gurdwara of Sikhism located in Amritsar.",
            "lat": 31.6200,
            "lng": 74.8765
        },
        {
            "name": "Jallianwala Bagh",
            "description": "Historic garden and memorial of national importance.",
            "lat": 31.6205,
            "lng": 74.8797
        },
        {
            "name": "Wagah Border",
            "description": "Famous border crossing between India and Pakistan.",
            "lat": 31.6047,
            "lng": 74.5747
        },
        # Arunachal Pradesh
        {
            "name": "Tawang Monastery",
            "description": "Largest monastery in India and second largest in the world.",
            "lat": 27.5859,
            "lng": 91.8757
        },
        {
            "name": "Ita Fort",
            "description": "Ancient fort with oval-shaped brick structure.",
            "lat": 27.0844,
            "lng": 93.6053
        },
        {
            "name": "Golden Pagoda",
            "description": "Buddhist temple known for its Burmese architecture.",
            "lat": 27.4833,
            "lng": 95.9833
        },
        # Madhya Pradesh
        {
            "name": "Khajuraho Temples",
            "description": "UNESCO World Heritage site known for its nagara-style architecture.",
            "lat": 24.8318,
            "lng": 79.9199
        },
        {
            "name": "Gwalior Fort",
            "description": "Historic fortress and architectural marvel.",
            "lat": 26.2322,
            "lng": 78.1691
        },
        {
            "name": "Orchha Fort",
            "description": "Historical site with multiple temples and palaces.",
            "lat": 25.3505,
            "lng": 78.6409
        },
        # Uttarakhand
        {
            "name": "Badrinath Temple",
            "description": "One of the holiest Hindu temples dedicated to Vishnu.",
            "lat": 30.7433,
            "lng": 79.4938
        },
        {
            "name": "Katarmal Sun Temple",
            "description": "Ancient sun temple from the 9th century.",
            "lat": 29.6366,
            "lng": 79.6266
        },
        # Himachal Pradesh
        {
            "name": "Kangra Fort",
            "description": "Oldest dated fort in India with rich history.",
            "lat": 32.0999,
            "lng": 76.2691
        },
        {
            "name": "Tabo Monastery",
            "description": "Ancient monastery known as the 'Ajanta of the Himalayas'.",
            "lat": 32.0935,
            "lng": 78.3872
        },
        # West Bengal
        {
            "name": "Victoria Memorial",
            "description": "Magnificent marble building dedicated to Queen Victoria.",
            "lat": 22.5448,
            "lng": 88.3426
        },
        {
            "name": "Hazarduari Palace",
            "description": "Palace with 1000 doors in Murshidabad.",
            "lat": 24.1765,
            "lng": 88.2801
        },
        {
            "name": "Bishnupur Terracotta Temples",
            "description": "Group of temples known for terracotta architecture.",
            "lat": 23.0795,
            "lng": 87.3198
        },
        # Jammu and Kashmir
        {
            "name": "Hari Parbat Fort",
            "description": "Historic fort overlooking Srinagar.",
            "lat": 34.1069,
            "lng": 74.8152
        },
        {
            "name": "Pari Mahal",
            "description": "Seven-terraced garden near Srinagar.",
            "lat": 34.0998,
            "lng": 74.8808
        },
        # Odisha
        {
            "name": "Konark Sun Temple",
            "description": "13th-century sun temple, UNESCO World Heritage site.",
            "lat": 19.8876,
            "lng": 86.0945
        },
        {
            "name": "Lingaraja Temple",
            "description": "Ancient temple dedicated to Lord Shiva.",
            "lat": 20.2359,
            "lng": 85.8320
        },
        # Gujarat
        {
            "name": "Rani ki Vav",
            "description": "Intricately designed stepwell, UNESCO World Heritage site.",
            "lat": 23.8593,
            "lng": 72.1023
        },
        {
            "name": "Dwarkadhish Temple",
            "description": "Ancient temple dedicated to Lord Krishna.",
            "lat": 22.2376,
            "lng": 68.9674
        },
        # Telangana
        {
            "name": "Charminar",
            "description": "Iconic monument and mosque in Hyderabad.",
            "lat": 17.3616,
            "lng": 78.4747
        },
        {
            "name": "Golconda Fort",
            "description": "Medieval fort and former diamond trading center.",
            "lat": 17.3833,
            "lng": 78.4011
        },
        {
            "name": "Warangal Fort",
            "description": "13th-century fort with impressive architecture.",
            "lat": 18.0006,
            "lng": 79.5881
        }
    ]

    # Add nearby hotels data
    hotels = [
        # Agra Hotels
        {
            "name": "The Oberoi Amarvilas",
            "description": "5-star luxury hotel with Taj Mahal views, 600m from Taj Mahal",
            "lat": 27.1731,
            "lng": 78.0484,
            "category": "Luxury"
        },
        {
            "name": "ITC Mughal",
            "description": "5-star hotel with Mughal architecture, near Taj Mahal",
            "lat": 27.1662,
            "lng": 78.0298,
            "category": "Luxury"
        },
        # Delhi Hotels
        {
            "name": "The Imperial",
            "description": "Historic 5-star hotel in central Delhi",
            "lat": 28.6264,
            "lng": 77.2189,
            "category": "Luxury"
        },
        {
            "name": "The Taj Mahal Hotel",
            "description": "Luxury hotel near India Gate",
            "lat": 28.6030,
            "lng": 77.2289,
            "category": "Luxury"
        },
        # Jaipur Hotels
        {
            "name": "Rambagh Palace",
            "description": "Former royal residence turned luxury hotel",
            "lat": 26.8980,
            "lng": 75.8183,
            "category": "Heritage"
        },
        {
            "name": "Taj Jai Mahal Palace",
            "description": "Heritage hotel with 18 acres of gardens",
            "lat": 26.9126,
            "lng": 75.8124,
            "category": "Heritage"
        },
        # Mumbai Hotels
        {
            "name": "The Taj Mahal Palace",
            "description": "Iconic 5-star hotel near Gateway of India",
            "lat": 18.9217,
            "lng": 72.8332,
            "category": "Luxury"
        },
        {
            "name": "The Oberoi Mumbai",
            "description": "Luxury hotel with sea views",
            "lat": 18.9257,
            "lng": 72.8212,
            "category": "Luxury"
        },
        # Udaipur Hotels
        {
            "name": "Taj Lake Palace",
            "description": "Luxury hotel in middle of Lake Pichola",
            "lat": 24.5753,
            "lng": 73.6808,
            "category": "Heritage"
        },
        # Varanasi Hotels
        {
            "name": "Taj Ganges",
            "description": "5-star hotel with modern amenities",
            "lat": 25.3176,
            "lng": 83.0065,
            "category": "Luxury"
        },
        # Goa Hotels
        {
            "name": "Taj Fort Aguada Resort",
            "description": "Luxury resort near Fort Aguada",
            "lat": 15.4977,
            "lng": 73.7637,
            "category": "Resort"
        },
        {
            "name": "Park Hyatt Goa Resort",
            "description": "Beachfront luxury resort",
            "lat": 15.2993,
            "lng": 73.9137,
            "category": "Resort"
        },
        # Kerala Hotels
        {
            "name": "Kumarakom Lake Resort",
            "description": "Luxury backwater resort",
            "lat": 9.5977,
            "lng": 76.4216,
            "category": "Resort"
        },
        {
            "name": "The Leela Kovalam",
            "description": "Cliff-top beach resort",
            "lat": 8.3809,
            "lng": 76.9781,
            "category": "Resort"
        },
        # Amritsar Hotels
        {
            "name": "Taj Swarna",
            "description": "Luxury hotel near Golden Temple",
            "lat": 31.6336,
            "lng": 74.8723,
            "category": "Luxury"
        },
        # Hyderabad Hotels
        {
            "name": "Taj Falaknuma Palace",
            "description": "Former Nizam's palace turned luxury hotel",
            "lat": 17.3328,
            "lng": 78.4677,
            "category": "Heritage"
        },
        {
            "name": "ITC Kohenur",
            "description": "Modern luxury hotel in HITEC City",
            "lat": 17.4275,
            "lng": 78.3461,
            "category": "Luxury"
        }
    ]

    return render_template("map.html", 
                         user=current_user, 
                         sites=heritage_sites,
                         hotels=hotels,
                         google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@views.route('/booking')
@login_required
def booking():
    today_date = datetime.now().strftime('%Y-%m-%d')
    # Get a default guide for the template
    default_guide = Guide.query.first()
    return render_template("booking.html", 
                         user=current_user, 
                         today_date=today_date,
                         guide=default_guide)

@views.route('/book_visit', methods=['POST'])
@login_required
def book_visit():
    if request.method == 'POST':
        # Get form data
        monument = request.form.get('monument')
        visit_date = request.form.get('visit_date')
        visitors = request.form.get('visitors')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        special_requests = request.form.get('special_requests')
        
        # Create new booking
        booking = Booking(
            monument_name=monument,
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d'),
            visitors=int(visitors),
            total_amount=float(visitors) * 1500,  # Base price per person
            name=name,
            email=email,
            phone=phone,
            special_requests=special_requests,
            user_id=current_user.id,
            status='Confirmed'  # Set as confirmed since this is a demo
        )
        
        try:
            db.session.add(booking)
            db.session.commit()
            flash('Booking confirmed successfully!', 'success')
            return redirect(url_for('views.booking_history'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your booking.', 'error')
            return redirect(url_for('views.booking'))

    return redirect(url_for('views.booking'))

@views.route('/booking-history')
@login_required
def booking_history():
    # Get all bookings for the current user
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('booking_history.html', 
                         user=current_user,
                         bookings=bookings)


@views.route('/guide/assign-package', methods=['POST'])
@login_required
def assign_package():
    if not current_user.is_guide:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    package_id = data.get('package_id')
    
    booking = Booking.query.get(package_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Package not found'}), 404
        
    if booking.guide_id:
        return jsonify({'success': False, 'message': 'Package already assigned'}), 400
        
    booking.guide_id = current_user.id
    db.session.commit()
    
    return jsonify({'success': True})

@views.route('/guide/update-booking-status', methods=['POST'])
@login_required
def update_booking_status():
    if not current_user.is_guide:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    booking_id = data.get('booking_id')
    status = data.get('status')
    
    booking = Booking.query.get(booking_id)
    if not booking or booking.guide_id != current_user.id:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
    booking.status = status
    db.session.commit()
    
    return jsonify({'success': True})

@views.route('/guide-dashboard')
@login_required
def guide_dashboard():
    if not current_user.is_guide:
        flash('Access denied. You are not registered as a guide.', 'error')
        return redirect(url_for('views.home'))
    
    guide = Guide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        flash('Guide profile not found.', 'error')
        return redirect(url_for('views.home'))

    # Get pending requests (paid bookings without a guide)
    pending_requests = Booking.query.filter_by(
        status='Successful',
        guide_id=None
    ).all()

    # Get accepted tours
    accepted_tours = Booking.query.filter_by(
        guide_id=guide.id,
        status='Confirmed'
    ).all()

    # Calculate total earnings
    total_earnings = sum(tour.total_amount for tour in accepted_tours)

    # Get guide's products
    products = Merchandise.query.filter_by(guide_id=guide.id).all()

    # List of states in India
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
        "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
        "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]

    return render_template(
        'guide_dashboard.html',
        user=current_user,
        guide=guide,
        pending_requests=pending_requests,
        accepted_tours=accepted_tours,
        total_earnings=total_earnings,
        states=states,
        products=products
    )

@views.route('/guide/handle-request', methods=['POST'])
@login_required
def handle_request():
    if not current_user.is_guide:
        return jsonify({'status': 'error', 'error': 'Not authorized'})

    data = request.get_json()
    request_id = data.get('request_id')
    action = data.get('action')

    booking = Booking.query.get(request_id)
    if not booking:
        return jsonify({'status': 'error', 'error': 'Booking not found'})

    guide = Guide.query.filter_by(user_id=current_user.id).first()
    
    try:
        if action == 'accept':
            booking.guide_id = guide.id
            booking.status = 'Confirmed'
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Tour request accepted successfully!'
            })
        elif action == 'reject':
            # Handle rejection logic if needed
            return jsonify({
                'status': 'success',
                'message': 'Tour request rejected'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)})

@views.route('/accept-booking/<int:booking_id>', methods=['POST'])
@login_required
def accept_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    guide = Guide.query.filter_by(user_id=current_user.id).first()
    
    if guide and booking:
        booking.guide_id = guide.id
        booking.status = 'accepted'
        db.session.commit()
        flash('Booking accepted successfully!', 'success')
    else:
        flash('Error accepting booking', 'error')
    
    return redirect(url_for('views.guide_dashboard'))

@views.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('my_bookings.html', bookings=bookings)

@views.route('/api/booking-payment', methods=['POST'])
@login_required
def handle_booking_payment():
    data = request.get_json()
    
    try:
        booking_id = data.get('bookingId')
        amount = float(data.get('amount', 0))
        payment_method = data.get('paymentMethod')
        
        # Get the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'status': 'error', 'error': 'Booking not found'})
            
        # Verify booking belongs to current user
        if booking.user_id != current_user.id:
            return jsonify({'status': 'error', 'error': 'Unauthorized'})

        # Process payment (demo version)
        if payment_method in ['credit', 'debit']:
            card_number = data.get('cardNumber')
            expiry = data.get('expiry')
            cvv = data.get('cvv')
            
            if not all([card_number, expiry, cvv]):
                return jsonify({'status': 'error', 'error': 'Missing card details'})
                
        elif payment_method == 'upi':
            upi_id = data.get('upiId')
            if not upi_id:
                return jsonify({'status': 'error', 'error': 'Missing UPI ID'})

        # If payment is successful, update booking status
        booking.status = 'Confirmed'
        db.session.commit()
                
        return jsonify({
            'status': 'success',
            'message': 'Payment processed successfully',
            'amount': amount,
            'method': payment_method
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)})

@views.route('/api/demo-payment', methods=['POST'])
@login_required
def demo_payment():
    data = request.get_json()
    
    try:
        booking_id = data.get('bookingId')
        amount = data.get('amount')
        payment_method = data.get('paymentMethod')
        
        # Simulate payment processing delay
        time.sleep(2)
        
        # Simulate success (90% success rate)
        success = random.random() < 0.9
        
        if success:
            # Update booking status
            booking = Booking.query.get(booking_id)
            if booking and booking.user_id == current_user.id:
                booking.status = 'Confirmed'
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Payment Successful!',
                    'transaction_id': f'TXN{random.randint(100000, 999999)}',
                    'amount': amount,
                    'method': payment_method
                })
        else:
            error_messages = [
                "Card declined by bank",
                "Insufficient funds",
                "Network error",
                "UPI service temporarily unavailable"
            ]
            return jsonify({
                'status': 'error',
                'error': random.choice(error_messages)
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@views.route('/api/cancel-booking', methods=['POST'])
@login_required
def cancel_booking():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        # Get the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({
                'status': 'error',
                'error': 'Booking not found'
            })
            
        # Verify booking belongs to current user
        if booking.user_id != current_user.id:
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized'
            })
            
        # Check if booking can be cancelled (not already cancelled)
        if booking.status == 'cancelled':
            return jsonify({
                'status': 'error',
                'error': 'Booking is already cancelled'
            })
            
        # Update booking status to cancelled
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Booking cancelled successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@views.route('/api/process-booking-payment', methods=['POST'])
@login_required
def process_booking_payment():
    data = request.get_json()
    
    try:
        # Get payment and booking details
        booking_data = data.get('bookingData', {})
        payment_method = data.get('paymentMethod')
        
        # Create new booking
        new_booking = Booking(
            user_id=current_user.id,
            monument_name=booking_data.get('monument'),
            booking_date=datetime.now(),
            visit_date=datetime.strptime(booking_data.get('visit_date'), '%Y-%m-%d'),
            visitors=int(booking_data.get('visitors')),
            total_amount=float(booking_data.get('amount')),
            status='Successful',  # Set initial status
            special_requests=booking_data.get('special_requests'),
            name=booking_data.get('name'),
            email=booking_data.get('email'),
            phone=booking_data.get('phone')
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        # Send WhatsApp confirmation
        booking_details = {
            'id': new_booking.id,
            'name': new_booking.name,
            'monument_name': new_booking.monument_name,
            'visit_date': new_booking.visit_date,
            'visitors': new_booking.visitors,
            'total_amount': new_booking.total_amount
        }
        
        success, message = send_booking_confirmation(new_booking.phone, booking_details)
        if not success:
            print(f"Failed to send WhatsApp message: {message}")
        
        return jsonify({
            'status': 'success',
            'message': 'Payment successful and booking confirmed!',
            'booking_id': new_booking.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@views.route('/itihaas-coins')
@login_required
def itihaas_coins():
    # Get transaction history from bookings
    transactions = []
    for booking in current_user.bookings:
        reward_coins = int(booking.total_amount * 0.1)
        transactions.append({
            'type': f'Reward for booking {booking.monument_name}',
            'date': booking.visit_date,
            'amount': reward_coins,
            'is_credit': True
        })
    
    # Sort transactions by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('itihaas_coins.html', transactions=transactions)

@views.route('/guide/manage-package', methods=['POST'])
@login_required
def manage_package():
    print("Debug: Starting manage_package...")
    if not current_user.is_guide:
        print("Debug: User is not a guide")
        return jsonify({'status': 'error', 'error': 'Not authorized'}), 403

    print("Debug: Getting guide profile...")
    guide = Guide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        print("Debug: Guide profile not found")
        return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

    data = request.get_json()
    print(f"Debug: Received data: {data}")
    
    try:
        # Validate required fields
        required_fields = ['state', 'name', 'description', 'duration', 'price', 'includes']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'error': f'Missing required field: {field}'}), 400

        if data.get('id'):  # Update existing package
            print(f"Debug: Updating package {data['id']}")
            package = TourPackage.query.get(data['id'])
            if not package or package.guide_id != guide.id:
                return jsonify({'status': 'error', 'error': 'Package not found'}), 404
            
            package.state = data['state']
            package.name = data['name']
            package.description = data['description']
            package.duration = data['duration']
            package.price = float(data['price'])
            package.includes = data['includes']
        else:  # Create new package
            print("Debug: Creating new package")
            package = TourPackage(
                guide_id=guide.id,
                state=data['state'],
                name=data['name'],
                description=data['description'],
                duration=data['duration'],
                price=float(data['price']),
                includes=data['includes'],
                is_active=True
            )
            db.session.add(package)

        db.session.commit()
        print("Debug: Successfully saved package")
        
        package_dict = package.to_dict()
        if not package_dict:
            raise Exception("Failed to convert package to dictionary")
            
        return jsonify({
            'status': 'success',
            'message': 'Package saved successfully',
            'package': package_dict
        })
    except Exception as e:
        print(f"Debug: Error in manage_package: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)}), 500

@views.route('/guide/delete-package', methods=['POST'])
@login_required
def delete_package():
    if not current_user.is_guide:
        return jsonify({'status': 'error', 'error': 'Not authorized'}), 403

    guide = Guide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

    data = request.get_json()
    try:
        package = TourPackage.query.get(data['package_id'])
        if not package or package.guide_id != guide.id:
            return jsonify({'status': 'error', 'error': 'Package not found'}), 404

        db.session.delete(package)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Package deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)}), 500

@views.route('/guide/get-packages')
@login_required
def get_guide_packages():
    try:
        print("Debug: Checking if user is guide...")
        if not current_user.is_guide:
            print("Debug: User is not a guide")
            return jsonify({'status': 'error', 'error': 'Not authorized'}), 403

        print("Debug: Getting guide profile...")
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        if not guide:
            print("Debug: Guide profile not found")
            return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

        print(f"Debug: Getting packages for guide ID {guide.id}...")
        packages = TourPackage.query.filter_by(guide_id=guide.id, is_active=True).all()
        print(f"Debug: Found {len(packages)} packages")
        
        package_list = []
        for package in packages:
            try:
                print(f"Debug: Converting package {package.id} to dict...")
                package_dict = package.to_dict()
                if package_dict:
                    package_list.append(package_dict)
                    print(f"Debug: Successfully added package {package.id} to list")
                else:
                    print(f"Debug: Package {package.id} to_dict() returned None")
            except Exception as e:
                print(f"Debug: Error converting package {package.id} to dict: {str(e)}")
                continue
        
        print(f"Debug: Returning {len(package_list)} packages")
        return jsonify({
            'status': 'success',
            'packages': package_list
        })
    except Exception as e:
        print(f"Debug: Error in get_guide_packages: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@views.route('/api/get-tour-packages')
def get_tour_packages():
    try:
        # Get all active packages grouped by state
        packages = TourPackage.query.filter_by(is_active=True).all()
        print(f"Found {len(packages)} active packages")  # Debug log
        
        packages_by_state = {}
        
        for package in packages:
            if package.state not in packages_by_state:
                packages_by_state[package.state] = []
            try:
                package_dict = package.to_dict()
                packages_by_state[package.state].append(package_dict)
            except Exception as e:
                print(f"Error converting package {package.id} to dict: {str(e)}")  # Debug log
                continue
        
        return jsonify({
            'status': 'success',
            'packages': packages_by_state
        })
    except Exception as e:
        print(f"Error in get_tour_packages: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@views.route('/api/update-profile-pic', methods=['POST'])
@login_required
def update_profile_pic():
    try:
        if 'profile_pic' not in request.files:
            return jsonify({'status': 'error', 'error': 'No file uploaded'}), 400
        
        file = request.files['profile_pic']
        if file.filename == '':
            return jsonify({'status': 'error', 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create a unique filename
            filename = secure_filename(f"{current_user.id}_{int(time.time())}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Update user's profile picture path
            current_user.profile_pic = url_for('static', filename=f'uploads/{filename}')
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'profile_pic_url': current_user.profile_pic
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@views.route('/seemore')
def seemore():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('seemore.html', reviews=reviews)

@views.route('/api/reviews/<int:review_id>/comments', methods=['GET'])
@login_required
def get_review_comments(review_id):
    try:
        # For demonstration purposes, we'll return some dummy comments
        # In a real implementation, you would fetch comments from a database
        comments = [
            {
                'id': 1,
                'text': 'Great review! I visited this monument last month and had a similar experience.',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user': {
                    'id': current_user.id,
                    'first_name': current_user.first_name,
                    'profile_pic': current_user.profile_pic
                }
            },
            {
                'id': 2,
                'text': 'Do you think it\'s worth visiting during the rainy season?',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user': {
                    'id': current_user.id,
                    'first_name': current_user.first_name,
                    'profile_pic': current_user.profile_pic
                }
            }
        ]
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@views.route('/api/reviews/<int:review_id>/comments', methods=['POST'])
@login_required
def add_review_comment(review_id):
    try:
        data = request.get_json()
        comment_text = data.get('text')
        
        if not comment_text:
            return jsonify({'error': 'Comment text is required'}), 400
            
        # For demonstration purposes, we're just returning the comment data
        # In a real implementation, you would save this to a database
        comment = {
            'id': random.randint(1, 1000),  # Generate a random ID for demo
            'text': comment_text,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': {
                'id': current_user.id,
                'first_name': current_user.first_name,
                'profile_pic': current_user.profile_pic
            }
        }
        
        return jsonify(comment)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@views.route('/admin-dashboard')
@login_required
def admin_dashboard():
    # Check if the current user is the admin
    if current_user.email != 'itihaasdairy@gmail.com':
        flash('Access denied. Admin privileges required.', category='error')
        return redirect(url_for('views.home'))
    
    # Get basic statistics
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_amount)).scalar() or 0
    
    # Get additional statistics
    active_guides = User.query.filter_by(is_guide=True).count()
    verified_users = User.query.filter_by(is_verified=True).count()
    pending_verifications = User.query.filter_by(is_verified=False).count()
    
    # Get today's bookings
    today = datetime.now().date()
    today_bookings = Booking.query.filter(
        db.func.date(Booking.booking_date) == today
    ).count()
    
    # Get pending approvals (bookings that need admin approval)
    pending_approvals = Booking.query.filter_by(status='Pending').count()
    
    # Get content statistics
    total_reviews = Review.query.count()
    active_vlogs = 5  # This should be replaced with actual vlog count from your database
    
    # Get recent activities (last 4 activities)
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(1).all()
    recent_users = User.query.order_by(User.id.desc()).limit(1).all()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(1).all()
    recent_guides = Guide.query.order_by(Guide.id.desc()).limit(1).all()
    
    # Combine recent activities
    recent_activities = []
    for booking in recent_bookings:
        recent_activities.append({
            'type': 'booking',
            'title': 'New Booking',
            'details': f"{booking.monument_name} - {booking.visitors} visitors",
            'date': booking.booking_date
        })
    for user in recent_users:
        recent_activities.append({
            'type': 'user',
            'title': 'New User Registration',
            'details': user.first_name,
            'date': datetime.now()
        })
    for review in recent_reviews:
        recent_activities.append({
            'type': 'review',
            'title': 'New Review',
            'details': f"{review.monument_name} - {review.rating} stars",
            'date': review.created_at
        })
    for guide in recent_guides:
        recent_activities.append({
            'type': 'guide',
            'title': 'New Guide Registration',
            'details': guide.name,
            'date': datetime.now()
        })
    
    # Sort activities by date and take the most recent 4
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:4]
    
    return render_template('admin.html', 
                         total_users=total_users,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         active_guides=active_guides,
                         verified_users=verified_users,
                         pending_verifications=pending_verifications,
                         today_bookings=today_bookings,
                         pending_approvals=pending_approvals,
                         total_reviews=total_reviews,
                         active_vlogs=active_vlogs,
                         recent_activities=recent_activities)
#10000000
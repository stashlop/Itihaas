from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from website.models import Guide, Order, OrderItem
from website.merchandise_models import Merchandise
from website import db

guide = Blueprint('guide', __name__)

# ... existing routes ...

@guide.route('/manage-merchandise', methods=['POST'])
@login_required
def manage_merchandise():
    try:
        data = request.get_json()
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        
        if not guide:
            return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

        if data.get('id'):  # Update existing merchandise
            merchandise = Merchandise.query.get(data['id'])
            if not merchandise or merchandise.guide_id != guide.id:
                return jsonify({'status': 'error', 'error': 'Merchandise not found'}), 404
            
            merchandise.name = data['name']
            merchandise.description = data['description']
            merchandise.price = data['price']
            merchandise.stock = data['stock']
            merchandise.category = data['category']
            merchandise.image_url = data['image_url']
        else:  # Create new merchandise
            merchandise = Merchandise(
                name=data['name'],
                description=data['description'],
                price=data['price'],
                stock=data['stock'],
                category=data['category'],
                image_url=data['image_url'],
                guide_id=guide.id
            )
            db.session.add(merchandise)

        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Merchandise saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)}), 500

@guide.route('/get-merchandise', methods=['GET'])
@login_required
def get_merchandise():
    try:
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        if not guide:
            return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

        merchandise = Merchandise.query.filter_by(guide_id=guide.id).all()
        return jsonify({
            'status': 'success',
            'merchandise': [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'stock': item.stock,
                'category': item.category,
                'image_url': item.image_url
            } for item in merchandise]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@guide.route('/delete-merchandise', methods=['POST'])
@login_required
def delete_merchandise():
    try:
        data = request.get_json()
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        
        if not guide:
            return jsonify({'status': 'error', 'error': 'Guide profile not found'}), 404

        merchandise = Merchandise.query.get(data['merchandise_id'])
        if not merchandise or merchandise.guide_id != guide.id:
            return jsonify({'status': 'error', 'error': 'Merchandise not found'}), 404

        db.session.delete(merchandise)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Merchandise deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'error': str(e)}), 500

@guide.route('/dashboard')
@login_required
def dashboard():
    guide = Guide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        return render_template('guide_dashboard.html', guide=None)

    # Get pending tour requests
    pending_requests = guide.get_pending_requests()
    
    # Get accepted tours
    accepted_tours = guide.get_accepted_tours()
    
    # Calculate total earnings
    total_earnings = guide.calculate_total_earnings()
    
    # Get merchandise orders
    merchandise_orders = Order.query.filter_by(guide_id=guide.id).order_by(Order.created_at.desc()).all()
    
    # Get guide's products
    products = Merchandise.query.filter_by(guide_id=guide.id).all()

    return render_template('guide_dashboard.html',
                         guide=guide,
                         pending_requests=pending_requests,
                         accepted_tours=accepted_tours,
                         total_earnings=total_earnings,
                         merchandise_orders=merchandise_orders,
                         products=products) 
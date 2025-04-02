from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .merchandise_models import Merchandise, CartItem, Order, OrderItem, Payment
from .models import Guide
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename

merchandise_bp = Blueprint('merchandise', __name__)

@merchandise_bp.route('/shop')
def shop():
    category = request.args.get('category')
    if category:
        products = Merchandise.query.filter_by(category=category).all()
    else:
        products = Merchandise.query.all()
    return render_template('merchandise/shop.html', products=products)

@merchandise_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Merchandise.query.get_or_404(product_id)
    related_products = Merchandise.query.filter_by(category=product.category).filter(Merchandise.id != product.id).limit(3).all()
    return render_template('merchandise/product_detail.html', product=product, related_products=related_products)

@merchandise_bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.merchandise.price for item in cart_items)
    return render_template('merchandise/cart.html', cart_items=cart_items, total=total)

@merchandise_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Merchandise.query.get_or_404(product_id)
    
    if product.stock < quantity:
        flash('Sorry, this item is out of stock!', 'error')
        return redirect(url_for('merchandise.product_detail', product_id=product_id))
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        merchandise_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            merchandise_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Item added to cart successfully!', 'success')
    return redirect(url_for('merchandise.cart'))

@merchandise_bp.route('/update-cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    return redirect(url_for('merchandise.cart'))

@merchandise_bp.route('/remove-from-cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('merchandise.cart'))

@merchandise_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('merchandise.cart'))
        
        total_amount = sum(item.quantity * item.merchandise.price for item in cart_items)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            payment_status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4()) if payment_method != 'cod' else None
        )
        db.session.add(payment)
        
        # Create order items and update stock
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                merchandise_id=cart_item.merchandise_id,
                quantity=cart_item.quantity,
                price=cart_item.merchandise.price
            )
            db.session.add(order_item)
            
            # Update stock
            cart_item.merchandise.stock -= cart_item.quantity
        
        # Clear cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        
        # Handle payment based on method
        if payment_method == 'cod':
            flash('Order placed successfully! Payment will be collected on delivery.', 'success')
        else:
            # Here you would typically integrate with a payment gateway
            # For now, we'll simulate a successful payment
            payment.status = 'completed'
            order.payment_status = 'completed'
            order.status = 'processing'
            db.session.commit()
            flash('Payment successful! Your order has been placed.', 'success')
        
        return redirect(url_for('merchandise.order_confirmation', order_id=order.id))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.merchandise.price for item in cart_items)
    return render_template('merchandise/checkout.html', cart_items=cart_items, total=total)

@merchandise_bp.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return render_template('merchandise/order_confirmation.html', order=order)

@merchandise_bp.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('merchandise/order_history.html', orders=orders)

@merchandise_bp.route('/add-product', methods=['POST'])
@login_required
def add_product():
    try:
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        if not guide:
            flash('Guide profile not found', 'error')
            return redirect(url_for('views.guide_dashboard'))

        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category')
        
        # Handle image upload
        if 'image' not in request.files:
            flash('No image uploaded', 'error')
            return redirect(url_for('views.guide_dashboard'))
            
        image = request.files['image']
        if image.filename == '':
            flash('No image selected', 'error')
            return redirect(url_for('views.guide_dashboard'))
            
        if image:
            filename = secure_filename(image.filename)
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the image
            image_path = os.path.join(upload_dir, filename)
            image.save(image_path)
            image_url = url_for('static', filename=f'uploads/{filename}')
        
        # Create new product
        product = Merchandise(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image_url=image_url,
            guide_id=guide.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('views.guide_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding product: {str(e)}', 'error')
        return redirect(url_for('views.guide_dashboard'))

@merchandise_bp.route('/edit-product', methods=['POST'])
@login_required
def edit_product():
    try:
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        if not guide:
            flash('Guide profile not found', 'error')
            return redirect(url_for('views.guide_dashboard'))

        product_id = request.form.get('product_id')
        product = Merchandise.query.get_or_404(product_id)
        
        # Verify product belongs to guide
        if product.guide_id != guide.id:
            flash('Unauthorized to edit this product', 'error')
            return redirect(url_for('views.guide_dashboard'))
        
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category = request.form.get('category')
        
        # Handle image upload if new image is provided
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            filename = secure_filename(image.filename)
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the image
            image_path = os.path.join(upload_dir, filename)
            image.save(image_path)
            product.image_url = url_for('static', filename=f'uploads/{filename}')
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('views.guide_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating product: {str(e)}', 'error')
        return redirect(url_for('views.guide_dashboard'))

@merchandise_bp.route('/api/product/<int:product_id>')
@login_required
def get_product(product_id):
    guide = Guide.query.filter_by(user_id=current_user.id).first()
    if not guide:
        return jsonify({'error': 'Guide profile not found'}), 404

    product = Merchandise.query.get_or_404(product_id)
    if product.guide_id != guide.id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category,
        'image_url': product.image_url
    })

@merchandise_bp.route('/api/product/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    try:
        guide = Guide.query.filter_by(user_id=current_user.id).first()
        if not guide:
            return jsonify({'error': 'Guide profile not found'}), 404

        product = Merchandise.query.get_or_404(product_id)
        if product.guide_id != guide.id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500 
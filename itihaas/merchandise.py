"""Merchandise shop: catalogue, cart, checkout and guide product management."""
from __future__ import annotations

import logging
import uuid

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .extensions import db
from .merchandise_models import CartItem, Merchandise, Order, OrderItem, Payment
from .utils import clean_text, current_guide, json_error, parse_float, parse_int, save_image_upload

merchandise_bp = Blueprint("merchandise", __name__)
log = logging.getLogger(__name__)

PAYMENT_METHODS = {"upi", "card", "cod"}
CATEGORIES = ("clothing", "accessories", "souvenirs", "books", "art")


def _cart_items():
    return CartItem.query.filter_by(user_id=current_user.id).all()


def _cart_total(items) -> float:
    return sum(item.quantity * item.merchandise.price for item in items if item.merchandise)


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
@merchandise_bp.route("/shop")
def shop():
    category = request.args.get("category")
    query = Merchandise.query
    if category:
        query = query.filter_by(category=category)
    products = query.order_by(Merchandise.created_at.desc()).all()
    categories = [row[0] for row in db.session.query(Merchandise.category).distinct().order_by(Merchandise.category) if row[0]]
    return render_template("merchandise/shop.html", products=products, categories=categories, active_category=category)


@merchandise_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.get_or_404(Merchandise, product_id)
    related_products = (
        Merchandise.query.filter_by(category=product.category).filter(Merchandise.id != product.id).limit(3).all()
    )
    return render_template("merchandise/product_detail.html", product=product, related_products=related_products)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
@merchandise_bp.route("/cart")
@login_required
def cart():
    items = _cart_items()
    return render_template("merchandise/cart.html", cart_items=items, total=_cart_total(items))


@merchandise_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = db.get_or_404(Merchandise, product_id)
    max_qty = current_app.config["MAX_CART_QUANTITY"]
    quantity = parse_int(request.form.get("quantity", 1), minimum=1, maximum=max_qty)
    if quantity is None:
        flash(f"Please choose a quantity between 1 and {max_qty}.", "error")
        return redirect(url_for("merchandise.product_detail", product_id=product_id))

    item = CartItem.query.filter_by(user_id=current_user.id, merchandise_id=product_id).first()
    new_quantity = quantity + (item.quantity if item else 0)
    if (product.stock or 0) < new_quantity:
        flash(f"Sorry, only {product.stock or 0} left in stock.", "error")
        return redirect(url_for("merchandise.product_detail", product_id=product_id))

    if item:
        item.quantity = new_quantity
    else:
        db.session.add(CartItem(user_id=current_user.id, merchandise_id=product_id, quantity=quantity))
    db.session.commit()
    flash(f"Added {product.name} to your cart.", "success")
    return redirect(url_for("merchandise.cart"))


def _owned_cart_item(item_id) -> CartItem:
    item = db.get_or_404(CartItem, item_id)
    if item.user_id != current_user.id:
        abort(403)
    return item


@merchandise_bp.route("/update-cart/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    item = _owned_cart_item(item_id)
    quantity = parse_int(request.form.get("quantity"), default=1, minimum=0,
                         maximum=current_app.config["MAX_CART_QUANTITY"])
    if quantity is None:
        flash("Invalid quantity.", "error")
    elif quantity == 0:
        db.session.delete(item)
    elif item.merchandise and quantity > (item.merchandise.stock or 0):
        flash(f"Only {item.merchandise.stock} of {item.merchandise.name} available.", "error")
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for("merchandise.cart"))


@merchandise_bp.route("/remove-from-cart/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    db.session.delete(_owned_cart_item(item_id))
    db.session.commit()
    flash("Item removed from your cart.", "info")
    return redirect(url_for("merchandise.cart"))


# ---------------------------------------------------------------------------
# Checkout & orders
# ---------------------------------------------------------------------------
@merchandise_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = _cart_items()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect(url_for("merchandise.shop"))

    if request.method == "GET":
        return render_template("merchandise/checkout.html", cart_items=items, total=_cart_total(items))

    shipping_address = clean_text(request.form.get("shipping_address"), 1000)
    payment_method = clean_text(request.form.get("payment_method"), 20).lower()
    if len(shipping_address) < 10:
        flash("Please enter a complete shipping address.", "error")
        return redirect(url_for("merchandise.checkout"))
    if payment_method not in PAYMENT_METHODS:
        flash("Please choose a payment method.", "error")
        return redirect(url_for("merchandise.checkout"))

    # Verify stock for every line before touching anything.
    for item in items:
        if not item.merchandise or (item.merchandise.stock or 0) < item.quantity:
            name = item.merchandise.name if item.merchandise else "An item"
            flash(f"{name} no longer has enough stock. Please update your cart.", "error")
            return redirect(url_for("merchandise.cart"))

    total_amount = _cart_total(items)
    paid_online = payment_method != "cod"
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
        # Online payments are simulated and always succeed in this demo.
        payment_status="completed" if paid_online else "pending",
        status="processing" if paid_online else "pending",
    )
    db.session.add(order)
    db.session.flush()

    db.session.add(Payment(
        order_id=order.id,
        amount=total_amount,
        payment_method=payment_method,
        transaction_id=str(uuid.uuid4()) if paid_online else None,
        status="completed" if paid_online else "pending",
    ))
    for item in items:
        db.session.add(OrderItem(order_id=order.id, merchandise_id=item.merchandise_id,
                                 quantity=item.quantity, price=item.merchandise.price))
        item.merchandise.stock -= item.quantity
        db.session.delete(item)
    db.session.commit()

    flash("Payment successful! Your order has been placed." if paid_online
          else "Order placed! Payment will be collected on delivery.", "success")
    return redirect(url_for("merchandise.order_confirmation", order_id=order.id))


@merchandise_bp.route("/order-confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = db.get_or_404(Order, order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template("merchandise/order_confirmation.html", order=order)


@merchandise_bp.route("/orders")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("merchandise/order_history.html", orders=orders)


# ---------------------------------------------------------------------------
# Guide product management
# ---------------------------------------------------------------------------
def _product_fields(form) -> tuple[dict | None, str | None]:
    fields = {
        "name": clean_text(form.get("name"), 150),
        "description": clean_text(form.get("description"), 5000),
        "price": parse_float(form.get("price"), minimum=0, maximum=1_000_000),
        "stock": parse_int(form.get("stock"), minimum=0, maximum=100_000),
        "category": clean_text(form.get("category"), 50).lower(),
    }
    if not fields["name"] or not fields["description"] or not fields["category"]:
        return None, "Name, description and category are required."
    if fields["price"] is None or fields["stock"] is None:
        return None, "Price and stock must be valid, non-negative numbers."
    return fields, None


@merchandise_bp.route("/add-product", methods=["POST"])
@login_required
def add_product():
    guide = current_guide()
    if not guide:
        flash("Only guides can add products.", "error")
        return redirect(url_for("views.home"))

    fields, error = _product_fields(request.form)
    image_url = save_image_upload(request.files.get("image"), prefix=f"product{guide.id}_")
    if not error and not image_url:
        error = "Please upload a product image (png, jpg, gif or webp)."
    if error:
        flash(error, "error")
        return redirect(url_for("views.guide_dashboard"))

    db.session.add(Merchandise(guide_id=guide.id, image_url=image_url, **fields))
    db.session.commit()
    flash("Product added successfully!", "success")
    return redirect(url_for("views.guide_dashboard"))


@merchandise_bp.route("/edit-product", methods=["POST"])
@login_required
def edit_product():
    guide = current_guide()
    if not guide:
        flash("Only guides can edit products.", "error")
        return redirect(url_for("views.home"))

    product = db.get_or_404(Merchandise, parse_int(request.form.get("product_id"), default=0))
    if product.guide_id != guide.id:
        abort(403)

    fields, error = _product_fields(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("views.guide_dashboard"))
    for key, value in fields.items():
        setattr(product, key, value)

    upload = request.files.get("image")
    if upload and upload.filename:
        image_url = save_image_upload(upload, prefix=f"product{guide.id}_")
        if not image_url:
            flash("Unsupported image type — other changes were saved.", "error")
        else:
            product.image_url = image_url

    db.session.commit()
    flash("Product updated successfully!", "success")
    return redirect(url_for("views.guide_dashboard"))


def _guide_product(product_id):
    guide = current_guide()
    if not guide:
        return None, json_error("Guide profile not found.", 404)
    product = db.get_or_404(Merchandise, product_id)
    if product.guide_id != guide.id:
        return None, json_error("Unauthorized.", 403)
    return product, None


@merchandise_bp.route("/api/product/<int:product_id>")
@login_required
def get_product(product_id):
    product, error = _guide_product(product_id)
    if error:
        return error
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category": product.category,
        "image_url": product.image_url,
    })


@merchandise_bp.route("/api/product/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):
    product, error = _guide_product(product_id)
    if error:
        return error
    if product.order_items:
        # Keep order history intact: hide the product instead of deleting it.
        product.stock = 0
        db.session.commit()
        return jsonify({"success": True, "archived": True})
    CartItem.query.filter_by(merchandise_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True})

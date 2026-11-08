"""Demo data for local development (``flask --app itihaas seed``)."""
from __future__ import annotations

from .extensions import db
from .merchandise_models import Merchandise
from .models import Guide, User

STORE_EMAIL = "store@itihaas.local"
PLACEHOLDER_IMAGE = "/static/img/placeholder-product.svg"

DEMO_PRODUCTS = [
    ("Classic Kurta", "Traditional Indian kurta made from premium cotton fabric. Perfect for both casual and formal occasions.", 1299.00, 50, "clothing"),
    ("Silk Saree", "Elegant silk saree with intricate zari work. A perfect blend of traditional and contemporary design.", 3999.00, 30, "clothing"),
    ("Cotton Salwar Kameez", "Comfortable and stylish salwar kameez set made from pure cotton. Ideal for daily wear.", 1499.00, 40, "clothing"),
    ("Designer Sherwani", "Luxurious sherwani with detailed embroidery work. Perfect for weddings and special occasions.", 5999.00, 25, "clothing"),
    ("Casual Palazzo Set", "Modern palazzo set with matching dupatta. Comfortable and fashionable for any occasion.", 999.00, 60, "clothing"),
    ("Taj Mahal Marble Miniature", "Hand-finished marble replica of the Taj Mahal, crafted by artisans in Agra.", 1899.00, 35, "souvenirs"),
    ("Block-Printed Tote Bag", "Jaipur hand block-printed cotton tote with natural dyes.", 649.00, 80, "accessories"),
    ("Heritage Postcard Set", "Set of 12 illustrated postcards featuring UNESCO World Heritage Sites of India.", 299.00, 120, "souvenirs"),
]


def _store_guide() -> Guide:
    """A system account that owns the demo catalogue. It has no password and cannot log in."""
    user = User.query.filter_by(email=STORE_EMAIL).first()
    if user is None:
        user = User(email=STORE_EMAIL, first_name="Itihaas Store", password=None, is_guide=True, is_verified=False)
        db.session.add(user)
        db.session.flush()
    guide = Guide.query.filter_by(user_id=user.id).first()
    if guide is None:
        guide = Guide(user_id=user.id, name="Itihaas Store", experience=0, languages="English, Hindi")
        db.session.add(guide)
        db.session.flush()
    return guide


def seed_merchandise() -> int:
    """Insert demo products that don't exist yet. Returns how many were added."""
    guide = _store_guide()
    added = 0
    for name, description, price, stock, category in DEMO_PRODUCTS:
        if Merchandise.query.filter_by(name=name).first():
            continue
        db.session.add(Merchandise(
            name=name, description=description, price=price, stock=stock,
            category=category, image_url=PLACEHOLDER_IMAGE, guide_id=guide.id,
        ))
        added += 1
    db.session.commit()
    return added

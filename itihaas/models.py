"""Core database models."""
from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta

from flask import current_app
from flask_login import UserMixin
from sqlalchemy.sql import func

from .extensions import db


def utcnow() -> datetime:
    """Naive UTC timestamp (SQLite stores naive datetimes).

    Replaces the deprecated ``datetime.utcnow()``.
    """
    return datetime.now(UTC).replace(tzinfo=None)


VERIFICATION_CODE_TTL = timedelta(minutes=10)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    profile_pic = db.Column(db.String(500))  # Store the path to the profile picture
    is_guide = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_code_timestamp = db.Column(db.DateTime(timezone=True))
    notes = db.relationship('Note')
    bookings = db.relationship('Booking', backref='user', lazy=True)
    guide_info = db.relationship('Guide', backref='user', uselist=False)
    itihaas_coins = db.relationship('ItihaasCoins', backref='user', uselist=False)

    @property
    def is_admin(self) -> bool:
        """Admins are configured through the ``ADMIN_EMAILS`` environment variable."""
        admins = current_app.config.get("ADMIN_EMAILS", [])
        return bool(self.email) and self.email.lower() in admins

    @property
    def coin_balance(self) -> int:
        return self.itihaas_coins.coins if self.itihaas_coins else 0

    def generate_verification_code(self) -> str:
        """Create a cryptographically secure 6-digit code valid for 10 minutes."""
        self.verification_code = f"{secrets.randbelow(1_000_000):06d}"
        self.verification_code_timestamp = utcnow()
        return self.verification_code

    def verify_code(self, code: str | None) -> bool:
        if not code or not self.verification_code or not self.verification_code_timestamp:
            return False
        issued = self.verification_code_timestamp.replace(tzinfo=None)
        if utcnow() - issued > VERIFICATION_CODE_TTL:
            return False
        if not hmac.compare_digest(self.verification_code, code.strip()):
            return False
        self.is_verified = True
        self.verification_code = None
        self.verification_code_timestamp = None
        return True

# New UNESCO-related models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    sites = db.relationship('Site', backref='category', lazy=True)

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    sites = db.relationship('Site', backref='region', lazy=True)

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    sites = db.relationship('Site', secondary='site_state')

class IsoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    name = db.Column(db.String(150))
    sites = db.relationship('Site', backref='iso_code', lazy=True)

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    iso_code_id = db.Column(db.Integer, db.ForeignKey('iso_code.id'))
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

class SiteState(db.Model):
    __tablename__ = 'site_state'
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), primary_key=True)

class SiteIsoCode(db.Model):
    __tablename__ = 'site_iso_code'
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), primary_key=True)
    iso_code_id = db.Column(db.Integer, db.ForeignKey('iso_code.id'), primary_key=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monument_name = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=utcnow)
    visit_date = db.Column(db.Date, nullable=False)
    visitors = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    special_requests = db.Column(db.Text)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'))
    is_special_package = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(150), nullable=True)
    booking_type = db.Column(db.String(20), default='individual')

    def to_dict(self):
        return {
            'monument_name': self.monument_name,
            'booking_date': self.booking_date.strftime('%Y-%m-%d'),
            'visit_date': self.visit_date.strftime('%Y-%m-%d'),
            'visitors': self.visitors,
            'total_amount': self.total_amount,
            'status': self.status,
            'special_requests': self.special_requests,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'state': self.state,
            'booking_type': self.booking_type,
            'is_special_package': self.is_special_package
        }

# New model for tour guide details
class GuideDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    experience_years = db.Column(db.Integer)
    specializations = db.Column(db.String(500))
    languages = db.Column(db.String(200))
    available_locations = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    verified = db.Column(db.Boolean, default=False)

class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(500))
    experience = db.Column(db.Integer, default=0)
    languages = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    total_tours = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(500))
    description = db.Column(db.Text)
    guided_tours = db.relationship('Booking', backref='guide', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'profile_picture': self.profile_picture,
            'experience': self.experience,
            'languages': self.languages,
            'rating': self.rating,
            'total_tours': self.total_tours,
            'specialization': self.specialization,
            'description': self.description
        }

class ItihaasCoins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coins = db.Column(db.Integer, default=0)

    def __init__(self, user_id, coins=0):
        self.user_id = user_id
        self.coins = coins

    def can_afford(self, amount_in_coins):
        return self.coins >= amount_in_coins

    def use_coins(self, coins):
        if self.can_afford(coins):
            self.coins -= coins
            return True
        return False

    def add_coins(self, coins):
        self.coins += coins

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'reward' or 'payment'
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user = db.relationship('User', backref='transactions')

class TourPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    state = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)  # e.g., "Full Day (8 hours)"
    price = db.Column(db.Float, nullable=False)
    includes = db.Column(db.JSON, nullable=False)  # List of included items/services
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    guide = db.relationship('Guide', backref='tour_packages')

    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'price': float(self.price or 0),
            'includes': self.includes if isinstance(self.includes, list) else [],
            'guide_id': self.guide_id,
            'guide': self.guide.to_dict() if self.guide else None,
            'is_active': self.is_active,
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    monument_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=False)
    tags = db.Column(db.JSON)  # List of tags
    photos = db.Column(db.JSON)  # List of photo URLs
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user = db.relationship('User', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'monument_name': self.monument_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'tags': self.tags if self.tags else [],
            'photos': self.photos if self.photos else [],
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S') if self.created_at else None,
            'user': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'profile_pic': self.user.profile_pic,
            }
        }


class ReviewComment(db.Model):
    """A comment left by a user on a review."""

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    user = db.relationship('User')
    review = db.relationship('Review', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))

    MAX_LENGTH = 1000

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'user': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'profile_pic': self.user.profile_pic,
            },
        }

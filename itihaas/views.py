"""Main site pages, bookings, guides, reviews and the admin dashboard."""
from __future__ import annotations

import json
import logging
import random
import uuid
from datetime import date, datetime

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from . import coins
from .data.heritage import FESTIVAL_SITES, HERITAGE_HOTELS, HERITAGE_SITES, INDIAN_STATES
from .extensions import db
from .merchandise_models import Merchandise
from .models import Booking, Guide, Review, ReviewComment, TourPackage, Transaction, User, utcnow
from .translations import translations
from .utils import (
    admin_required,
    clean_text,
    current_guide,
    is_valid_email,
    json_error,
    parse_float,
    parse_int,
    save_image_upload,
)
from .whatsapp import send_booking_confirmation

views = Blueprint("views", __name__)
log = logging.getLogger(__name__)

# Booking status values already stored in existing databases. They are kept
# verbatim for compatibility; comparisons should be case-insensitive.
STATUS_PAID_AWAITING_GUIDE = "Successful"
STATUS_CONFIRMED = "Confirmed"
STATUS_CANCELLED = "cancelled"
GUIDE_SETTABLE_STATUSES = {"Confirmed", "Completed", "cancelled"}


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@views.route("/")
def home():
    return render_template("home.html")


@views.route("/about")
def about():
    return render_template("about.html")


@views.route("/vlog")
def vlog():
    return render_template("vlog.html")


@views.route("/news")
def news():
    return render_template("news.html", news_configured=bool(current_app.config.get("NEWS_API_KEY")))


@views.route("/seemore")
def seemore():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("seemore.html", reviews=reviews)


@views.route("/change-language", methods=["POST"])
def change_language():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang")
    if lang not in translations:
        return json_error("Unsupported language.")
    session["lang"] = lang
    return jsonify({"status": "success", "lang": lang})


@views.route("/health")
def health():
    """Liveness/readiness probe for hosting platforms."""
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        log.exception("Health check failed")
        return jsonify({"status": "error", "database": "unavailable"}), 503
    return jsonify({"status": "ok", "database": "ok"})


# ---------------------------------------------------------------------------
# Explore
# ---------------------------------------------------------------------------
@views.route("/index")
@login_required
def place():
    return render_template("index.html", festival_sites=FESTIVAL_SITES)


@views.route("/map")
@login_required
def map_view():
    return render_template(
        "map.html",
        sites=HERITAGE_SITES,
        hotels=HERITAGE_HOTELS,
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
    )


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
@views.route("/review")
@login_required
def review():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("review.html", reviews=reviews)


@views.route("/api/reviews", methods=["POST"])
@login_required
def create_review():
    monument_name = clean_text(request.form.get("monument_name"), 200)
    review_text = clean_text(request.form.get("review_text"), 5000)
    rating = parse_int(request.form.get("rating"), minimum=1, maximum=5)
    if not monument_name or not review_text or rating is None:
        return json_error("Monument, a 1–5 rating and review text are required.")

    try:
        tags = json.loads(request.form.get("tags", "[]"))
    except (TypeError, ValueError):
        tags = []
    tags = [clean_text(tag, 40) for tag in tags if isinstance(tag, str) and tag.strip()][:10]

    photos = []
    for file in request.files.getlist("photos")[:6]:
        url = save_image_upload(file, prefix="review_")
        if url:
            photos.append(url)

    review = Review(
        user_id=current_user.id,
        monument_name=monument_name,
        rating=rating,
        review_text=review_text,
        tags=tags,
        photos=photos,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review submitted successfully", "review": review.to_dict()}), 200


@views.route("/api/reviews/<int:review_id>/comments", methods=["GET"])
@login_required
def get_review_comments(review_id):
    db.get_or_404(Review, review_id)
    comments = (
        ReviewComment.query.filter_by(review_id=review_id).order_by(ReviewComment.created_at.asc()).all()
    )
    return jsonify([comment.to_dict() for comment in comments])


@views.route("/api/reviews/<int:review_id>/comments", methods=["POST"])
@login_required
def add_review_comment(review_id):
    db.get_or_404(Review, review_id)
    data = request.get_json(silent=True) or {}
    text = clean_text(data.get("text"), ReviewComment.MAX_LENGTH)
    if not text:
        return json_error("Comment text is required.")
    comment = ReviewComment(review_id=review_id, user_id=current_user.id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------
@views.route("/booking")
@login_required
def booking():
    return render_template(
        "booking.html",
        today_date=date.today().isoformat(),
        guide=Guide.query.first(),
    )


def _parse_visit_date(value) -> date | None:
    try:
        visit = datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    return visit if visit >= date.today() else None


@views.route("/book_visit", methods=["POST"])
@login_required
def book_visit():
    """Legacy form-based booking (fixed ₹1,500 per visitor)."""
    max_visitors = current_app.config["MAX_VISITORS_PER_BOOKING"]
    visitors = parse_int(request.form.get("visitors"), minimum=1, maximum=max_visitors)
    visit_date = _parse_visit_date(request.form.get("visit_date"))
    monument = clean_text(request.form.get("monument"), 100)
    name = clean_text(request.form.get("name"), 100)
    email = clean_text(request.form.get("email"), 120)
    phone = clean_text(request.form.get("phone"), 20)

    if not all([visitors, visit_date, monument, name, phone]) or not is_valid_email(email):
        flash("Please fill in all booking details with a valid future date.", "error")
        return redirect(url_for("views.booking"))

    booking = Booking(
        monument_name=monument,
        visit_date=visit_date,
        visitors=visitors,
        total_amount=visitors * 1500,
        name=name,
        email=email,
        phone=phone,
        special_requests=clean_text(request.form.get("special_requests"), 1000),
        user_id=current_user.id,
        status=STATUS_CONFIRMED,
    )
    db.session.add(booking)
    db.session.commit()
    flash("Booking confirmed successfully!", "success")
    return redirect(url_for("views.booking_history"))


@views.route("/booking-history")
@login_required
def booking_history():
    bookings = (
        Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    )
    return render_template("booking_history.html", bookings=bookings)


@views.route("/my-bookings")
@login_required
def my_bookings():
    # Previously rendered a template that never existed (HTTP 500).
    return redirect(url_for("views.booking_history"))


@views.route("/api/process-booking-payment", methods=["POST"])
@login_required
def process_booking_payment():
    """Create a booking after a (simulated) payment.

    Request body::

        {"bookingData": {...}, "paymentMethod": "card|upi|coins", "coinsToUse": 0}

    Coins are validated against the server-side balance; rewards are computed
    here — never trusted from the client.
    """
    data = request.get_json(silent=True) or {}
    booking_data = data.get("bookingData") or {}
    payment_method = clean_text(data.get("paymentMethod"), 20).lower()
    config = current_app.config

    if payment_method not in {"card", "upi", "coins"}:
        return json_error("Unsupported payment method.")

    visitors = parse_int(booking_data.get("visitors"), minimum=1, maximum=config["MAX_VISITORS_PER_BOOKING"])
    amount = parse_float(booking_data.get("amount"), minimum=1, maximum=config["MAX_BOOKING_AMOUNT"])
    visit_date = _parse_visit_date(booking_data.get("visit_date"))
    monument = clean_text(booking_data.get("monument") or booking_data.get("monument_name"), 100)
    name = clean_text(booking_data.get("name"), 100)
    email = clean_text(booking_data.get("email"), 120)
    phone = clean_text(booking_data.get("phone"), 20)

    errors = []
    if visitors is None:
        errors.append("visitors")
    if amount is None:
        errors.append("amount")
    if visit_date is None:
        errors.append("visit date (must be today or later)")
    if not monument:
        errors.append("monument")
    if not name:
        errors.append("name")
    if not is_valid_email(email):
        errors.append("e-mail")
    if not phone:
        errors.append("phone")
    if errors:
        return json_error("Please provide a valid " + ", ".join(errors) + ".")

    reference = f"BKG-{uuid.uuid4().hex[:10].upper()}"
    requested_coins = parse_int(data.get("coinsToUse"), default=0, minimum=0) or 0
    if payment_method == "coins":
        requested_coins = max(requested_coins, int(amount))

    new_booking = Booking(
        user_id=current_user.id,
        monument_name=monument,
        booking_date=utcnow(),
        visit_date=visit_date,
        visitors=visitors,
        total_amount=amount,
        status=STATUS_PAID_AWAITING_GUIDE,
        special_requests=clean_text(booking_data.get("special_requests"), 1000),
        name=name,
        email=email,
        phone=phone,
        state=clean_text(booking_data.get("state"), 150) or None,
        booking_type="package" if booking_data.get("booking_type") == "package" else "individual",
        is_special_package=booking_data.get("booking_type") == "package",
    )
    db.session.add(new_booking)

    coins_used = coins.spend(current_user.id, requested_coins, amount, reference)
    amount_due = round(amount - coins_used, 2)
    if payment_method == "coins" and amount_due > 0:
        db.session.rollback()
        return json_error(
            "Not enough Itihaas Coins to cover this booking.",
            balance=current_user.coin_balance,
        )

    coins_earned = coins.award(current_user.id, coins.reward_for(amount_due), reference)
    db.session.commit()

    _notify_whatsapp(new_booking)

    return jsonify({
        "status": "success",
        "message": "Payment successful and booking confirmed!",
        "booking_id": new_booking.id,
        "transaction_id": reference,
        "amount": amount,
        "amount_paid": amount_due,
        "coins_used": coins_used,
        "coins_earned": coins_earned,
        "new_balance": current_user.coin_balance,
    })


def _notify_whatsapp(booking: Booking) -> None:
    if not current_app.config.get("WHATSAPP_ENABLED"):
        return
    ok, message = send_booking_confirmation(booking.phone, {
        "id": booking.id,
        "name": booking.name,
        "monument_name": booking.monument_name,
        "visit_date": booking.visit_date,
        "visitors": booking.visitors,
        "total_amount": booking.total_amount,
    })
    if ok:
        booking.whatsapp_sent = True
        db.session.commit()
    else:
        log.warning("WhatsApp confirmation for booking %s failed: %s", booking.id, message)


def _owned_booking(booking_id) -> Booking | None:
    booking_id = parse_int(booking_id, minimum=1)
    if booking_id is None:
        return None
    booking = db.session.get(Booking, booking_id)
    return booking if booking and booking.user_id == current_user.id else None


@views.route("/api/booking-payment", methods=["POST"])
@login_required
def handle_booking_payment():
    """Mark an existing booking as paid (simulated card/UPI payment)."""
    data = request.get_json(silent=True) or {}
    booking = _owned_booking(data.get("bookingId"))
    if not booking:
        return json_error("Booking not found.", 404)

    method = data.get("paymentMethod")
    if method in ("credit", "debit", "card") and not all(data.get(k) for k in ("cardNumber", "expiry", "cvv")):
        return json_error("Missing card details.")
    if method == "upi" and not data.get("upiId"):
        return json_error("Missing UPI ID.")

    booking.status = STATUS_CONFIRMED
    db.session.commit()
    return jsonify({"status": "success", "message": "Payment processed successfully",
                    "amount": booking.total_amount, "method": method})


@views.route("/api/demo-payment", methods=["POST"])
@login_required
def demo_payment():
    """Simulated payment gateway with a small random failure rate (demo only)."""
    data = request.get_json(silent=True) or {}
    booking = _owned_booking(data.get("bookingId"))
    if not booking:
        return json_error("Booking not found.", 404)

    if random.random() >= 0.9:
        return json_error(random.choice([
            "Card declined by bank",
            "Insufficient funds",
            "Network error",
            "UPI service temporarily unavailable",
        ]), 402)

    booking.status = STATUS_CONFIRMED
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Payment Successful!",
        "transaction_id": f"TXN{uuid.uuid4().hex[:8].upper()}",
        "amount": booking.total_amount,
        "method": data.get("paymentMethod"),
    })


@views.route("/api/cancel-booking", methods=["POST"])
@login_required
def cancel_booking():
    data = request.get_json(silent=True) or {}
    booking = _owned_booking(data.get("booking_id"))
    if not booking:
        return json_error("Booking not found.", 404)
    if (booking.status or "").lower() == STATUS_CANCELLED:
        return json_error("Booking is already cancelled.")
    booking.status = STATUS_CANCELLED
    db.session.commit()
    return jsonify({"status": "success", "message": "Booking cancelled successfully"})


# ---------------------------------------------------------------------------
# Itihaas Coins
# ---------------------------------------------------------------------------
@views.route("/itihaas-coins")
@login_required
def itihaas_coins():
    ledger = (
        Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(100).all()
    )
    transactions = [
        {
            "type": "Reward" if txn.transaction_type == coins.REWARD else "Spent on booking",
            "reference": txn.transaction_id,
            "date": txn.date,
            "amount": txn.amount,
            "is_credit": txn.transaction_type == coins.REWARD,
        }
        for txn in ledger
    ]
    return render_template("itihaas_coins.html", transactions=transactions, balance=current_user.coin_balance)


# ---------------------------------------------------------------------------
# Guides
# ---------------------------------------------------------------------------
@views.route("/guide-dashboard")
@login_required
def guide_dashboard():
    if not current_user.is_guide:
        flash("Access denied. You are not registered as a guide.", "error")
        return redirect(url_for("views.home"))

    guide = current_guide()
    if not guide:
        flash("Guide profile not found.", "error")
        return redirect(url_for("views.home"))

    pending_requests = Booking.query.filter_by(status=STATUS_PAID_AWAITING_GUIDE, guide_id=None).all()
    accepted_tours = Booking.query.filter_by(guide_id=guide.id, status=STATUS_CONFIRMED).all()
    return render_template(
        "guide_dashboard.html",
        guide=guide,
        pending_requests=pending_requests,
        accepted_tours=accepted_tours,
        total_earnings=sum(tour.total_amount for tour in accepted_tours),
        states=INDIAN_STATES,
        products=Merchandise.query.filter_by(guide_id=guide.id).all(),
    )


def _claim_booking(guide: Guide, booking: Booking | None) -> str | None:
    """Assign an unclaimed booking to a guide. Returns an error message or None."""
    if not booking:
        return "Booking not found."
    if booking.guide_id and booking.guide_id != guide.id:
        return "This tour has already been accepted by another guide."
    if (booking.status or "").lower() == STATUS_CANCELLED:
        return "This booking was cancelled."
    booking.guide_id = guide.id
    booking.status = STATUS_CONFIRMED
    db.session.commit()
    return None


@views.route("/guide/handle-request", methods=["POST"])
@login_required
def handle_request():
    guide = current_guide()
    if not guide:
        return json_error("Not authorized.", 403)

    data = request.get_json(silent=True) or {}
    booking = db.session.get(Booking, parse_int(data.get("request_id"), default=0))
    action = data.get("action")
    if action == "accept":
        error = _claim_booking(guide, booking)
        if error:
            return json_error(error, 409 if booking else 404)
        return jsonify({"status": "success", "message": "Tour request accepted successfully!"})
    if action == "reject":
        if not booking:
            return json_error("Booking not found.", 404)
        return jsonify({"status": "success", "message": "Tour request rejected"})
    return json_error("Unknown action.")


@views.route("/guide/assign-package", methods=["POST"])
@login_required
def assign_package():
    guide = current_guide()
    if not guide:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    data = request.get_json(silent=True) or {}
    booking = db.session.get(Booking, parse_int(data.get("package_id"), default=0))
    error = _claim_booking(guide, booking)
    if error:
        return jsonify({"success": False, "message": error}), 404 if not booking else 400
    return jsonify({"success": True})


@views.route("/guide/update-booking-status", methods=["POST"])
@login_required
def update_booking_status():
    guide = current_guide()
    if not guide:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    data = request.get_json(silent=True) or {}
    booking = db.session.get(Booking, parse_int(data.get("booking_id"), default=0))
    # Previously compared guide_id with the *user* id, so it never matched.
    if not booking or booking.guide_id != guide.id:
        return jsonify({"success": False, "message": "Booking not found"}), 404
    status = data.get("status")
    if status not in GUIDE_SETTABLE_STATUSES:
        return jsonify({"success": False, "message": "Invalid status"}), 400
    booking.status = status
    db.session.commit()
    return jsonify({"success": True})


@views.route("/accept-booking/<int:booking_id>", methods=["POST"])
@login_required
def accept_booking(booking_id):
    guide = current_guide()
    if not guide:
        flash("Only registered guides can accept bookings.", "error")
        return redirect(url_for("views.home"))
    error = _claim_booking(guide, db.session.get(Booking, booking_id))
    flash(error or "Booking accepted successfully!", "error" if error else "success")
    return redirect(url_for("views.guide_dashboard"))


def _validate_package(data: dict) -> tuple[dict | None, str | None]:
    required = ["state", "name", "description", "duration", "price", "includes"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return None, f"Missing required field: {missing[0]}"
    price = parse_float(data.get("price"), minimum=0, maximum=current_app.config["MAX_BOOKING_AMOUNT"])
    if price is None:
        return None, "Price must be a positive number."
    includes = data.get("includes")
    if isinstance(includes, str):
        includes = [item.strip() for item in includes.split(",")]
    if not isinstance(includes, list):
        return None, "Includes must be a list."
    return {
        "state": clean_text(data["state"], 150),
        "name": clean_text(data["name"], 200),
        "description": clean_text(data["description"], 5000),
        "duration": clean_text(data["duration"], 100),
        "price": price,
        "includes": [clean_text(item, 120) for item in includes if str(item).strip()][:30],
    }, None


@views.route("/guide/manage-package", methods=["POST"])
@login_required
def manage_package():
    guide = current_guide()
    if not guide:
        return json_error("Not authorized.", 403)

    data = request.get_json(silent=True) or {}
    fields, error = _validate_package(data)
    if error:
        return json_error(error)

    if data.get("id"):
        package = db.session.get(TourPackage, parse_int(data["id"], default=0))
        if not package or package.guide_id != guide.id:
            return json_error("Package not found.", 404)
        for key, value in fields.items():
            setattr(package, key, value)
    else:
        package = TourPackage(guide_id=guide.id, is_active=True, **fields)
        db.session.add(package)

    db.session.commit()
    return jsonify({"status": "success", "message": "Package saved successfully", "package": package.to_dict()})


@views.route("/guide/delete-package", methods=["POST"])
@login_required
def delete_package():
    guide = current_guide()
    if not guide:
        return json_error("Not authorized.", 403)
    data = request.get_json(silent=True) or {}
    package = db.session.get(TourPackage, parse_int(data.get("package_id"), default=0))
    if not package or package.guide_id != guide.id:
        return json_error("Package not found.", 404)
    db.session.delete(package)
    db.session.commit()
    return jsonify({"status": "success", "message": "Package deleted successfully"})


@views.route("/guide/get-packages")
@login_required
def get_guide_packages():
    guide = current_guide()
    if not guide:
        return json_error("Not authorized.", 403)
    packages = TourPackage.query.filter_by(guide_id=guide.id, is_active=True).all()
    return jsonify({"status": "success", "packages": [package.to_dict() for package in packages]})


@views.route("/api/get-tour-packages")
def get_tour_packages():
    packages_by_state: dict[str, list] = {}
    for package in TourPackage.query.filter_by(is_active=True).all():
        packages_by_state.setdefault(package.state, []).append(package.to_dict())
    return jsonify({"status": "success", "packages": packages_by_state})


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
@views.route("/api/update-profile-pic", methods=["POST"])
@login_required
def update_profile_pic():
    file = request.files.get("profile_pic")
    if not file or not file.filename:
        return json_error("No file selected.")
    url = save_image_upload(file, prefix=f"user{current_user.id}_")
    if not url:
        return json_error("Invalid file type. Allowed types: png, jpg, jpeg, gif, webp.")
    current_user.profile_pic = url
    db.session.commit()
    return jsonify({"status": "success", "profile_pic_url": url})


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
def _monthly_revenue(months: int = 6) -> dict:
    """Booking revenue (excluding cancellations) for the last ``months`` calendar months."""
    today = date.today()
    keys = []
    year, month = today.year, today.month
    for _ in range(months):
        keys.append((year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    keys.reverse()
    start = date(*keys[0], 1)

    totals = dict.fromkeys(keys, 0.0)
    rows = (
        db.session.query(Booking.booking_date, Booking.total_amount)
        .filter(Booking.booking_date >= start, db.func.lower(Booking.status) != STATUS_CANCELLED)
        .all()
    )
    for booked_at, amount in rows:
        key = (booked_at.year, booked_at.month)
        if key in totals:
            totals[key] += amount or 0
    return {
        "labels": [date(y, m, 1).strftime("%b %Y") for y, m in keys],
        "data": [round(totals[key], 2) for key in keys],
    }


@views.route("/admin-dashboard")
@login_required
@admin_required
def admin_dashboard():
    today = date.today()
    recent_activities = []

    for booking in Booking.query.order_by(Booking.booking_date.desc()).limit(4):
        recent_activities.append({"type": "booking", "title": "New Booking",
                                  "details": f"{booking.monument_name} - {booking.visitors} visitors",
                                  "date": booking.booking_date})
    for review in Review.query.order_by(Review.created_at.desc()).limit(4):
        recent_activities.append({"type": "review", "title": "New Review",
                                  "details": f"{review.monument_name} - {review.rating} stars",
                                  "date": review.created_at})
    for txn in Transaction.query.order_by(Transaction.date.desc()).limit(4):
        recent_activities.append({"type": "user", "title": "Coin Transaction",
                                  "details": f"{txn.transaction_type.title()} · {txn.amount} coins",
                                  "date": txn.date})
    recent_activities = [a for a in recent_activities if a["date"]]
    recent_activities.sort(key=lambda a: a["date"].replace(tzinfo=None), reverse=True)

    return render_template(
        "admin.html",
        revenue_chart=_monthly_revenue(months=6),
        total_users=User.query.count(),
        total_bookings=Booking.query.count(),
        total_revenue=db.session.query(db.func.sum(Booking.total_amount)).scalar() or 0,
        active_guides=User.query.filter_by(is_guide=True).count(),
        verified_users=User.query.filter_by(is_verified=True).count(),
        pending_verifications=User.query.filter_by(is_verified=False).count(),
        today_bookings=Booking.query.filter(db.func.date(Booking.booking_date) == today.isoformat()).count(),
        pending_approvals=Booking.query.filter_by(status="Pending").count(),
        total_reviews=Review.query.count(),
        total_products=Merchandise.query.count(),
        recent_activities=recent_activities[:4],
    )

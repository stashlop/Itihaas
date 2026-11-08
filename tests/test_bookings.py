"""Bookings, the Itihaas Coins ledger and guide workflows."""
from datetime import date, timedelta

import pytest

from itihaas.models import Booking, ItihaasCoins, Transaction


def booking_payload(**overrides):
    data = {
        "monument": "Taj Mahal",
        "state": "Uttar Pradesh",
        "visit_date": (date.today() + timedelta(days=7)).isoformat(),
        "visitors": 2,
        "amount": 1000,
        "name": "Asha",
        "email": "asha@example.com",
        "phone": "+91 98765 43210",
    }
    data.update(overrides)
    return data


def pay(client, method="card", coins=0, **overrides):
    return client.post("/api/process-booking-payment", json={
        "bookingData": booking_payload(**overrides), "paymentMethod": method, "coinsToUse": coins,
    })


def balance(user_id):
    wallet = ItihaasCoins.query.filter_by(user_id=user_id).first()
    return wallet.coins if wallet else 0


def test_card_payment_creates_booking_and_rewards_ten_percent(client, user):
    response = pay(client)
    data = response.get_json()
    assert response.status_code == 200, data
    assert data["coins_earned"] == 100 and data["new_balance"] == 100
    booking = Booking.query.one()
    assert booking.user_id == user.id and booking.status == "Successful" and booking.state == "Uttar Pradesh"
    assert Transaction.query.filter_by(user_id=user.id, transaction_type="reward").one().amount == 100


def test_coins_cover_part_of_a_booking(client, user):
    pay(client, amount=1000)                       # earn 100
    data = pay(client, coins=500, amount=300).get_json()  # can only use 100
    assert data["coins_used"] == 100
    assert data["amount_paid"] == 200
    assert data["coins_earned"] == 20              # reward only on the cash part
    assert balance(user.id) == 20


def test_paying_fully_with_coins(client, user):
    pay(client, amount=2000)                       # earn 200
    data = pay(client, method="coins", amount=150).get_json()
    assert data["status"] == "success"
    assert data["coins_used"] == 150 and data["amount_paid"] == 0 and data["coins_earned"] == 0
    assert balance(user.id) == 50


def test_insufficient_coins_creates_nothing(client, user):
    response = pay(client, method="coins", amount=500)
    assert response.status_code == 400
    assert Booking.query.count() == 0
    assert Transaction.query.count() == 0


@pytest.mark.parametrize("override", [
    {"visit_date": (date.today() - timedelta(days=1)).isoformat()},
    {"visit_date": "not-a-date"},
    {"visitors": 0},
    {"visitors": 500},
    {"amount": -5},
    {"amount": "abc"},
    {"email": "nope"},
    {"monument": ""},
])
def test_invalid_booking_data_is_rejected(client, user, override):
    assert pay(client, **override).status_code == 400
    assert Booking.query.count() == 0


def test_unknown_payment_method_rejected(client, user):
    assert pay(client, method="bitcoin").status_code == 400


def test_cancel_booking_only_by_owner(client, user, make_user, login):
    booking_id = pay(client).get_json()["booking_id"]
    client.get("/logout")
    make_user(email="other@example.com")
    login(email="other@example.com")
    assert client.post("/api/cancel-booking", json={"booking_id": booking_id}).status_code == 404
    client.get("/logout")
    login()
    assert client.post("/api/cancel-booking", json={"booking_id": booking_id}).status_code == 200
    assert client.post("/api/cancel-booking", json={"booking_id": booking_id}).status_code == 400


def test_my_bookings_redirects_to_history(client, user):
    response = client.get("/my-bookings")
    assert response.status_code == 302 and response.headers["Location"].endswith("/booking-history")


def test_coins_page_shows_ledger(client, user):
    pay(client)
    page = client.get("/itihaas-coins").get_data(as_text=True)
    assert "+100" in page and "Reward" in page


def test_guide_accepts_request_with_guide_id(client, user, make_user, login):
    booking_id = pay(client).get_json()["booking_id"]
    client.get("/logout")
    guide_user = make_user(email="guide@example.com", guide=True)
    login(email="guide@example.com")

    assert client.get("/guide-dashboard").status_code == 200
    response = client.post("/guide/handle-request", json={"request_id": booking_id, "action": "accept"})
    assert response.get_json()["status"] == "success"
    booking = Booking.query.filter_by(id=booking_id).one()
    assert booking.guide_id == guide_user.guide_info.id   # previously stored the user id
    assert booking.status == "Confirmed"

    ok = client.post("/guide/update-booking-status", json={"booking_id": booking_id, "status": "Completed"})
    assert ok.get_json() == {"success": True}
    bad = client.post("/guide/update-booking-status", json={"booking_id": booking_id, "status": "Hacked"})
    assert bad.status_code == 400


def test_second_guide_cannot_steal_accepted_tour(client, user, make_user, login):
    booking_id = pay(client).get_json()["booking_id"]
    client.get("/logout")
    make_user(email="g1@example.com", guide=True)
    make_user(email="g2@example.com", guide=True)
    login(email="g1@example.com")
    client.post("/guide/handle-request", json={"request_id": booking_id, "action": "accept"})
    client.get("/logout")
    login(email="g2@example.com")
    assert client.post("/guide/handle-request", json={"request_id": booking_id, "action": "accept"}).status_code == 409


def test_non_guides_cannot_use_guide_endpoints(client, user):
    assert client.post("/guide/handle-request", json={"request_id": 1, "action": "accept"}).status_code == 403
    assert client.get("/guide/get-packages").status_code == 403
    assert client.get("/guide-dashboard").status_code == 302


def test_guide_package_crud(client, make_user, login):
    make_user(email="guide@example.com", guide=True)
    login(email="guide@example.com")
    payload = {"state": "Delhi", "name": "Old Delhi Walk", "description": "Heritage walk", "duration": "Half day",
               "price": "1500", "includes": ["Guide", "Chai"]}
    created = client.post("/guide/manage-package", json=payload).get_json()
    assert created["status"] == "success"
    package_id = created["package"]["id"]

    public = client.get("/api/get-tour-packages").get_json()
    assert public["packages"]["Delhi"][0]["name"] == "Old Delhi Walk"

    assert client.post("/guide/manage-package", json={**payload, "price": "-1"}).status_code == 400
    assert client.post("/guide/delete-package", json={"package_id": package_id}).get_json()["status"] == "success"
    assert client.get("/guide/get-packages").get_json()["packages"] == []

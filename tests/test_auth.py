"""Sign-up, verification, login and authorisation."""
import re

from itihaas.models import Guide, GuideDetails, User
from tests.conftest import PASSWORD


def _signup(client, email="new@example.com", **overrides):
    data = {"email": email, "firstName": "Meera", "password1": "longpassword", "password2": "longpassword"}
    data.update(overrides)
    return client.post("/sign-up", data=data)


def test_signup_and_verify_flow(client, caplog):
    caplog.set_level("WARNING")
    response = _signup(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/verify-email")

    code = re.search(r"verification code for new@example.com is (\d{6})", caplog.text).group(1)
    assert client.post("/verify-email", data={"verification_code": "000000" if code != "000000" else "111111"}).status_code == 200
    response = client.post("/verify-email", data={"verification_code": code})
    assert response.status_code == 302

    user = User.query.filter_by(email="new@example.com").one()
    assert user.is_verified and user.verification_code is None
    assert client.get("/booking").status_code == 200  # logged in


def test_signup_validation(client):
    assert _signup(client, email="not-an-email").status_code == 200
    assert _signup(client, password1="short", password2="short").status_code == 200
    assert _signup(client, password2="different-pass").status_code == 200
    assert User.query.count() == 0


def test_signup_rejects_duplicate_email_case_insensitively(client, make_user):
    make_user(email="taken@example.com")
    _signup(client, email="TAKEN@example.com")
    assert User.query.count() == 1


def test_login_success_and_failure(client, make_user, login):
    make_user()
    assert login(password="wrong").status_code == 401
    response = login()
    assert response.status_code == 302


def test_login_email_is_case_insensitive(client, make_user, login):
    make_user(email="mixed@example.com")
    assert login(email="MIXED@Example.com").status_code == 302


def test_unverified_user_is_sent_to_verification(client, make_user, login):
    make_user(verified=False)
    response = login()
    assert response.headers["Location"].endswith("/verify-email")


def test_old_admin_backdoor_is_gone(client, login):
    response = login(email="itihaasdairy@gmail.com", password="12345678")
    assert response.status_code == 401
    assert User.query.filter_by(email="itihaasdairy@gmail.com").first() is None


def test_login_next_redirect_is_restricted_to_site(client, make_user):
    make_user()
    ok = client.post("/login?next=/shop", data={"email": "user@example.com", "password": PASSWORD})
    assert ok.headers["Location"] == "/shop"
    client.get("/logout")
    evil = client.post("/login?next=https://evil.example/", data={"email": "user@example.com", "password": PASSWORD})
    assert "evil.example" not in evil.headers["Location"]


def test_admin_dashboard_requires_configured_admin(client, make_user, login):
    make_user(email="user@example.com")
    make_user(email="admin@example.com")  # listed in TestingConfig.ADMIN_EMAILS
    login(email="user@example.com")
    assert client.get("/admin-dashboard").status_code == 403
    client.get("/logout")
    login(email="admin@example.com")
    response = client.get("/admin-dashboard")
    assert response.status_code == 200
    assert b"revenueChart" in response.data


def test_guide_signup_persists_professional_details(client):
    response = client.post("/guide-signup", data={
        "email": "guide@example.com", "firstName": "Ravi", "phone": "+91 98765 43210",
        "password1": "longpassword", "password2": "longpassword",
        "license": "LIC-123", "experience": "7",
        "languages": ["English", "Hindi"], "specializations": ["Religious Sites"],
        "locations": ["Taj Mahal", "Not A Real Site"],
    })
    assert response.status_code == 302
    user = User.query.filter_by(email="guide@example.com").one()
    guide = Guide.query.filter_by(user_id=user.id).one()
    details = GuideDetails.query.filter_by(user_id=user.id).one()
    assert user.is_guide
    assert guide.experience == 7 and guide.languages == "English, Hindi"
    assert details.license_number == "LIC-123"
    assert details.available_locations == "Taj Mahal"


def test_guide_signup_requires_licence_and_location(client):
    response = client.post("/guide-signup", data={
        "email": "g2@example.com", "firstName": "Ravi", "phone": "+91 98765 43210",
        "password1": "longpassword", "password2": "longpassword", "experience": "2", "languages": ["English"],
    })
    assert response.status_code == 200
    assert User.query.count() == 0


def test_verification_code_expires(app, make_user):
    from datetime import timedelta

    from itihaas.models import utcnow

    user = make_user(verified=False)
    code = user.generate_verification_code()
    user.verification_code_timestamp = utcnow() - timedelta(minutes=11)
    assert not user.verify_code(code)


def test_update_coins_ignores_client_rewards(client, user):
    response = client.post("/update-coins", json={"reward_coins": 1_000_000, "transaction_id": "x"})
    assert response.get_json() == {"success": True, "new_balance": 0}

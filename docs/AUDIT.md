# Itihaas — Repository Audit (Phase 1)

_Audit date: 2026-11-08 · Baseline commit: `c32b0b5`_

This document records the state of the repository **before** the modernization
work. Every finding below was confirmed by reading the code and/or running the
application with Flask's test client (Python 3.13, dependencies from
`requirements.txt`).

---

## 1. Purpose & core functionality

Itihaas is a Flask web application promoting Indian heritage tourism, built as
a "Colloquium 2025 – IT for Society" project. Features present in the code:

| Area | What exists |
| --- | --- |
| Accounts | Sign-up with 6-digit e-mail verification code, login/logout, profile picture upload |
| Tour guides | Guide sign-up, guide dashboard, tour packages (CRUD), accept tour requests |
| Monument booking | Multi-step booking UI with simulated card/UPI payment, booking history, cancellation |
| Itihaas Coins | Loyalty balance (10 % reward on bookings), coin redemption during booking |
| Map | Google Maps with 56 heritage sites and 17 heritage hotels, weather popups (OpenWeather) |
| Shop | Merchandise catalogue, cart, checkout (simulated payment), order history; guides can add products |
| Reviews | Review feed with ratings, tags, photo uploads; comment UI |
| Chatbot | Rule-based "Monuments Assistant" widget with curated monument data |
| Content | Home, About, Vlogs, Places/festival calendar, News page |
| i18n | 9 UI languages via a dictionary (`translations.py`) |
| Admin | Statistics dashboard |

## 2. Technology stack (as found)

- **Backend:** Flask 3.1.2, Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.43, Flask-Login, Flask-Mail, Flask-Migrate (no migrations directory), Flask-Babel (imported, never initialised)
- **NLP:** spaCy 3.8 + `en_core_web_sm` — loaded at start-up but **never used** anywhere
- **Database:** SQLite
- **Frontend:** Jinja2 templates with very large inline `<style>`/`<script>` blocks; Bootstrap **4.4.1 CSS + 4.0.0 JS** (mismatched), jQuery **3.2.1 slim**, Popper 1.12.9, Font Awesome 5.15.4, Swiper 8 (unpinned), Leaflet 1.9.4, Chart.js (unpinned), Splitting (unpinned)
- **3rd-party APIs:** Google Maps JS, OpenWeather, NewsAPI-shaped `/api/news` (no backend), Gmail SMTP, `pywhatkit` (WhatsApp desktop automation)

## 3. Folder structure (as found)

The repository root **is** the Python package (`__init__.py` at the root). It
only imports if the *parent* directory is on `sys.path` **and** the current
directory is the repo root (because of absolute `website.*` imports resolved
through a shim package). Cloning into a folder not named `Itihaas` breaks
`run.py`.

```
/ (package "Itihaas")
├── __init__.py, run.py, config.py
├── views.py (1,398 lines — routes + hard-coded map data)
├── auth.py, merchandise.py, chatbot.py (1,634 lines, HTML/CSS/JS in Python strings)
├── models.py, merchandise_models.py
├── guide.py, payment.py, automated_messaging.py, merchandise_data.py   ← dead / broken
├── models/merchandise.py                                                ← dead duplicate
├── website/ (import shim)
├── templates/ (≈20,000 lines)
├── instance/database.db   ← committed
├── email.log, __pycache__/*.pyc   ← committed
└── (no static/ directory)
```

## 4. Dependencies

| Package | Version | Finding |
| --- | --- | --- |
| spaCy, thinc, numpy, blis, … (≈30 packages) | various | Pulled in only for an unused `nlp` global. Hundreds of MB, slow installs. **Remove.** |
| `en_core_web_sm` | wheel URL | Same as above |
| flask-babel | 4.0.0 | Imported, never initialised. **Remove.** |
| Flask | 3.1.2 | 3.1.3 available (patch) |
| SQLAlchemy | 2.0.43 | 2.1 available — minor version with deprecations; stay on 2.0.x until Flask-SQLAlchemy supports 2.1 officially |
| pywhatkit, schedule, stripe | — | Imported by code but **missing** from requirements |
| Bootstrap JS 4.0.0 / CSS 4.4.1 | — | Mismatched versions; some pages load a second copy (4.6.0 bundle) |
| jQuery 3.2.1 slim | — | Known XSS advisories (CVE-2019-11358, CVE-2020-11022/11023); pages also load a second jQuery 3.6.0 |
| Swiper `@8`, Chart.js, Splitting | unpinned | Unpinned CDN URLs can change underneath the app |

## 5. Bugs & broken functionality (verified)

1. **Database path bug** — `SQLALCHEMY_DATABASE_URI='sqlite:///database.db'` resolves against Flask's instance path, which for this layout is `<parent-of-repo>/instance/`. The app writes its DB **outside the repository**; the committed `instance/database.db` is never used.
2. **`/news` returns 404** although it is linked in the navbar and `news.html` exists; `/api/news` (called by that page) does not exist.
3. **`/my-bookings` returns 500** — renders a non-existent `my_bookings.html`.
4. **`/api/add-coins` does not exist** — called by the unreachable "Add Money" modal in `base.html`.
5. **Coin payments never create a booking** — `processCoinsPayment()` only calls `/update-coins`.
6. **`/update-coins` 500s** on a duplicate `transaction_id` and records spending as a `reward` of 0.
7. **Guide actions use the wrong IDs** — `assign_package` stores a *user* id in `booking.guide_id`; `update_booking_status` compares `guide_id` to the *user* id; `handle_request` crashes when a guide profile is missing; `accept_booking` has no guide check.
8. **Checkout ignores stock** — quantities can drive `stock` negative; non-numeric quantities raise 500.
9. **`checkout.html` scripts never run** — uses `{% block scripts %}` which `base.html` does not define.
10. **Local sign-up is impossible without Gmail credentials** — if sending fails the new user is deleted.
11. **SMTP connection opened at application start-up** (`mail.connect()`), slowing boot and failing offline.
12. **Review comments are fake** — `GET` returns two hard-coded comments; `POST` is not persisted.
13. **Itihaas Coins page** derives "transactions" from bookings instead of the `Transaction` ledger, so it disagrees with the balance.
14. **Fresh installs have an empty shop** — no seed mechanism (`merchandise_data.py` is never called and would crash: plaintext password, list into a string column).
15. **Uploaded files overwrite each other** — review photos and product images keep the original filename.
16. **`static/` was never committed** — 95 referenced images/videos/audio files are missing, so every hero image, card image and video 404s.
17. Deprecated APIs: `datetime.utcnow()` (deprecated in Python 3.12), `Query.get()` (legacy in SQLAlchemy 2.0).

## 6. Security findings

| Severity | Finding |
| --- | --- |
| **Critical** | Hard-coded admin backdoor: a fixed e-mail and an 8-digit password in `auth.py` logged in as admin, auto-creating the account (`auth.py`). |
| **Critical** | Hard-coded `SECRET_KEY` (`'hjshjhdjah kjshkjdhjs'`) → session cookies can be forged. |
| **High** | Client decides coin rewards: any logged-in user can `POST /update-coins {"reward_coins": 1000000}`. |
| **High** | Committed SQLite DB contains real e-mail addresses and password hashes. |
| **High** | API keys committed in source: Google Maps key in `map.html`, OpenWeather key in `map.html`, Mapbox token in `.env.example`. These should be **rotated** — they remain in git history. |
| **High** | No CSRF protection on any form or JSON endpoint. |
| **Medium** | Debug mode on by default (`FLASK_DEBUG` defaults to `'1'`) → Werkzeug debugger (RCE) if exposed. |
| **Medium** | Raw exception text (incl. SQL) returned to clients. |
| **Medium** | XSS sinks: news articles (third-party content) and review comments are inserted with `innerHTML` unescaped. |
| **Medium** | Product image upload has no extension check; no `MAX_CONTENT_LENGTH`. |
| **Low** | Verification codes generated with `random` (not cryptographically secure); no security headers; `MAIL_DEBUG=True` logs SMTP traffic. |
| **Low** | Booking amount is supplied by the client (simulated payments only). |

## 7. Code quality & technical debt

- Business data (56 map sites, 17 hotels, monument encyclopaedia) hard-coded inside route functions and Python strings.
- `chatbot.py` embeds ~1,400 lines of HTML/CSS/JS in a Python string.
- Extensive `print()` debugging instead of logging.
- Duplicate code paths: `views.guide_dashboard` vs dead `guide.py`; two merchandise model files; three payment endpoints for the same flow.
- Unused models (`Note`, `Category`, `Region`, `State`, `IsoCode`, `Site`, `SiteState`, `SiteIsoCode`, `GuideDetails`) — kept for now, flagged for a future decision.
- No tests, no linting, no CI.

## 8. Does it run?

Yes, with caveats: after `pip install` (≈1 GB because of spaCy) and running
`python run.py` from inside a folder named `Itihaas`, the public pages return
200. Verified failures: `/news` 404, `/my-bookings` 500, `/update-coins` 500 on
repeat, empty shop, missing media everywhere, sign-up blocked without SMTP
credentials.

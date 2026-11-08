# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [2.2.0] — 2026-11-08

Design pass made with [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky (@heydamir), CC BY 4.0.

### Changed
- Home page rebuilt: headline set in the sky of the Taj Mahal photograph, plain copy that says
  what the product does, one primary and one secondary action, and the festival carousel
  replaced by a calm, dated strip of festival tours (soonest first, "On now" / "Next" markers).
- Monument coordinates as the design signature (hero caption and the sign-in panel).
- Warm neutral colour ramp; saffron is the only accent. Removed the gradient wordmark, glow on
  hover, gold glow on the headline, rainbow badges, colour washes, gradient chatbot launcher,
  uppercase tracked labels, hover lifts and image zooms, and nav icons.
- Two type families only (Poppins and Fraunces); headings at weight 500; tabular figures.
- Buttons use a 10px radius instead of pills; chatbot buttons use dark text on saffron (≈6:1).
- Sign-in panel uses a photograph of the Taj Mahal's reflecting pool instead of colour washes.

### Fixed
- Festival tours showed this year's dates, so by November eight of nine reported
  "already passed"; each tour now shows its next dates, including the Christmas–New Year
  trip that spans the turn of the year.
- Christmas tour duration was negative (its end date was in the wrong year).
- Removed the background-audio autoplay attempt on the home page.

### Added
- `itihaas/data/festivals.py` holds the festival tour data that used to live in inline JavaScript.
- A 10-second before/after video of the redesign: `docs/media/itihaas-unslop.mp4`.

## [2.1.0] — 2026-11-08

### Added
- 69 real photographs from Wikimedia Commons (61 monuments, festivals and places, 8 heritage
  hotels) in `itihaas/static/media/`, replacing the media that was never committed.
  All are freely licensed (CC0, public domain, CC BY, CC BY-SA).
- Photo credits page (`/credits`, linked in the footer) generated from
  `itihaas/data/media_credits.json`, with author, licence and source for every photo.
- Tests that fail if a bundled photo is missing or lacks complete attribution.
- Photo posters for the home and booking background videos (the videos themselves are still missing).

### Fixed
- The Places page rendered as a narrow four-column grid because the layout's `<main id="main">`
  collided with that page's own `#main` styles (the layout wrapper is now `#content`).
- The Places carousel used Windows-style relative paths (`static\taj.jpg`) that never loaded,
  and showed tutorial placeholder text ("Name Slider").
- Dead avatar and logo paths now point to bundled SVGs.

## [2.0.0] — 2026-11-08

Revival and modernisation of the 2025 project. See [docs/AUDIT.md](docs/AUDIT.md) for
the audit that guided these changes.

### Security
- Removed the hard-coded admin login backdoor; admins are configured with `ADMIN_EMAILS`.
- `SECRET_KEY` is read from the environment (required in production); debug mode is off by default.
- CSRF protection on all forms and JSON endpoints (Flask-WTF).
- Itihaas Coins are now awarded and spent only on the server; `/update-coins` ignores client-supplied rewards.
- API keys removed from templates; news and weather are proxied server-side.
  **The previously committed Google Maps, OpenWeather and Mapbox keys should be rotated** — they remain in git history.
- The committed SQLite database (containing personal data) is no longer tracked.
- Cryptographically secure verification codes; upload type/size validation with unique filenames;
  security headers; no raw exception messages returned to clients; reviews no longer expose e-mails;
  third-party news and user comments are HTML-escaped; card details are never submitted to the server.

### Added
- `/news` page backend and `/api/news`, `/api/weather` proxies with caching.
- Persisted review comments (`ReviewComment`) — previously hard-coded demo data.
- Itihaas Coins ledger page backed by the `Transaction` table.
- Real monthly revenue chart on the admin dashboard (previously fabricated numbers).
- Guide sign-up now stores licence, experience, languages, specialisations and covered sites.
- `flask seed`, `flask create-admin` and `flask whatsapp-dispatch` CLI commands.
- `/health` endpoint, `wsgi.py` for Gunicorn, custom 4xx/5xx error pages.
- Design system, toast notifications, footer, skip link, empty/loading/error states.
- pytest suite (102 tests), Ruff configuration and a GitHub Actions workflow.
- CONTRIBUTING, SECURITY, issue and pull-request templates.

### Changed
- Code moved into an importable `itihaas/` package with an application factory and
  environment-based configuration (`.env` supported).
- Redesigned navigation, authentication, shop, cart, checkout, orders, coins, news and error pages.
- Front-end libraries are self-hosted and pinned (Bootstrap 4.6.2, jQuery 3.7.1, Font Awesome 5.15.4,
  Swiper 8.4.7, Chart.js 4.4.7, Leaflet 1.9.4), replacing mismatched CDN copies.
- Coin rewards are calculated on the amount paid by card/UPI (not on the part paid with coins).
- Partial coin payments reserve coins and deduct them only when the remaining payment succeeds.
- Dependencies trimmed to direct, pinned requirements (Flask 3.1.3, SQLAlchemy 2.0.57).

### Fixed
- Database was created outside the repository because of the package layout.
- `/my-bookings` returned HTTP 500; `/news` returned 404.
- Paying fully with coins never created a booking.
- Guide actions mixed up user and guide IDs; any user could accept bookings.
- Checkout could drive stock negative; invalid quantities caused errors.
- Sign-up was impossible locally without SMTP; SMTP was contacted on every start-up.
- `.env` values were loaded after configuration was evaluated.
- 37 missing translation keys rendered as raw identifiers; the login e-mail label showed the contact address.
- Booking and history pages overflowed horizontally on phones; duplicate element IDs between the booking page and the Plan My Day modal.
- Deprecated `datetime.utcnow()` and `Query.get()` usage.

### Removed
- Unused spaCy/NLP stack (~30 packages) and Flask-Babel.
- Dead or broken modules: `guide.py`, `payment.py` (Stripe placeholders), `automated_messaging.py`,
  `models/merchandise.py`, the `website/` import shim, and the unreachable "Add Money" modal.

## [1.0.0] — 2025

Initial version built for Colloquium 2025 — IT for Society.

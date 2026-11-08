# Contributing to Itihaas

Thanks for your interest in improving Itihaas! This guide explains how to set up the
project, the standards we follow and how to propose changes.

## Ways to contribute

- 🐛 Report bugs with the **Bug report** issue template
- 💡 Suggest features with the **Feature request** template
- 🌐 Improve translations in `itihaas/translations.py` (many languages still fall back to English)
- 🧪 Add tests, improve accessibility or documentation
- 🛠️ Pick up an item from the roadmap in the README

For anything larger than a small fix, please open an issue first so we can agree on the approach.

## Development setup

```bash
git clone https://github.com/stashlop/Itihaas.git
cd Itihaas
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                # set FLASK_DEBUG=1 for development
flask --app itihaas seed                            # optional demo products
python run.py
```

With `FLASK_DEBUG=1` and no SMTP credentials, sign-up verification codes are printed in
the terminal.

## Before you open a pull request

```bash
ruff check .        # lint (ruff check . --fix fixes most issues)
pytest              # all tests must pass
```

CI runs the same checks on Python 3.11, 3.12 and 3.13.

### Checklist

- [ ] The change is focused — one feature or fix per pull request
- [ ] New behaviour is covered by tests in `tests/`
- [ ] `ruff check .` and `pytest` pass locally
- [ ] UI changes were checked at desktop **and** mobile widths (≈390 px) and include before/after screenshots
- [ ] No secrets, API keys, databases or uploaded files are committed
- [ ] Documentation (README, `.env.example`, CHANGELOG) is updated when behaviour or configuration changes

## Coding guidelines

**Python**
- Follow the existing structure: routes in blueprints, shared helpers in `utils.py`,
  reference data in `itihaas/data/`, configuration only via `config.py` / environment variables.
- Validate every input on the server (`parse_int`, `parse_float`, `clean_text`, …). Never
  trust amounts, coin values or ownership coming from the browser.
- Return errors with `json_error(...)` — never return raw exception messages to clients.
- Use `db.session.get(Model, id)` / `db.get_or_404(...)` rather than the legacy `Query.get()`.
- Add a short docstring to new modules and non-trivial functions.

**Templates & front end**
- Extend `base.html`; reuse design-system classes from `static/css/itihaas.css`
  (`ih-card`, `btn-ih`, `ih-input`, `empty-state`, …) instead of new one-off styles.
- Every form needs `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
  `fetch()` calls get the token automatically from `app.js`.
- Escape user or third-party content before inserting it with `innerHTML`
  (`Itihaas.escapeHtml`, `Itihaas.safeUrl`).
- Use translation keys (`{{ _('key') }}`) for user-facing text and add the English string
  to `translations.py`.
- Keep pages accessible: labels for inputs, `alt` text, visible focus, sufficient contrast.

**Front-end libraries** are self-hosted under `itihaas/static/vendor`. To upgrade one,
change the version in `scripts/vendor.sh`, run it (requires npm), then test the pages that
use the library.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(shop): add wishlist
fix(auth): reject expired verification codes
docs: explain PostgreSQL deployment
```

## Code of conduct

Be kind and respectful. Harassment or discrimination of any kind is not tolerated.

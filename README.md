# Itihaas

**A comprehensive platform for Indian monument booking and tourism promotion**

Itihaas is a Flask-based web application designed to promote tourism in India by enabling monument bookings, tour guide services, merchandise shopping, and interactive features like chatbots and reviews. Built for the Colloquium 2025 IT for Society project.

---

## Features

- 🏛️ **Monument Booking System** - Book visits to UNESCO heritage sites and monuments across India
- 🗺️ **Interactive Maps** - Explore monuments with Google Maps integration
- 👨‍🏫 **Tour Guide Services** - Connect with verified local guides and book tour packages
- 🛍️ **Merchandise Store** - Shop for cultural souvenirs, clothing, and accessories
- 💬 **AI Chatbot** - Get instant information about monuments and travel tips
- ⭐ **Reviews & Ratings** - Share experiences and read reviews from other travelers
- 🪙 **Itihaas Coins** - Loyalty rewards system for bookings and activities
- 📧 **Email Verification** - Secure account registration with email verification
- 🌐 **Multi-language Support** - Interface available in multiple languages
- 📱 **WhatsApp Notifications** - Booking confirmations via WhatsApp

---

## Tech Stack

- **Backend**: Flask (Python 3.12+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Email**: Flask-Mail with Gmail SMTP
- **NLP**: spaCy for natural language processing
- **Frontend**: HTML, CSS, JavaScript (Jinja2 templates)
- **Maps**: Google Maps API
- **Migrations**: Flask-Migrate (Alembic)

---

## Project Structure

```
Itihaas/
├── __init__.py              # Flask app factory and configuration
├── run.py                   # Application entry point
├── config.py                # Configuration settings
├── models.py                # Database models (User, Booking, Guide, etc.)
├── views.py                 # Main application routes
├── auth.py                  # Authentication routes (login, signup)
├── merchandise.py           # Merchandise/shop routes
├── chatbot.py               # Chatbot functionality
├── email_utils.py           # Email sending utilities
├── whatsapp.py              # WhatsApp integration
├── translations.py          # Multi-language support
├── website/                 # Package shim for imports
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── instance/                # Database file
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

---

## Installation

### Prerequisites

- Python 3.12 or higher
- pip and virtualenv
- Gmail account with App Password (for email features)
- Google Maps API key (for map features)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/stashlop/Itihaas.git
   cd Itihaas
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy language model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-gmail-app-password
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   FLASK_DEBUG=1
   FLASK_RUN_HOST=127.0.0.1
   FLASK_RUN_PORT=5000
   ```

   **Important Notes:**
   - For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
   - Enable 2-Step Verification in your Google Account first
   - Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)

6. **Initialize the database**
   ```bash
   python run.py
   ```
   The database will be created automatically on first run at `instance/database.db`

---

## Running the Application

### Option 1: Using run.py (Recommended)

```bash
python run.py
```

The app will start at `http://127.0.0.1:5000` by default.

### Option 2: Using Flask CLI

```bash
export FLASK_APP=Itihaas:create_app  # On Windows: set FLASK_APP=Itihaas:create_app
flask run --port 5000
```

### Development Mode

The app runs in debug mode by default when `FLASK_DEBUG=1` is set in `.env`. This enables:
- Auto-reloading on code changes
- Detailed error pages
- Debug toolbar

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `EMAIL_USER` | Gmail address for sending emails | No* | None |
| `EMAIL_PASSWORD` | Gmail App Password | No* | None |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | No* | None |
| `FLASK_DEBUG` | Enable debug mode (1 or 0) | No | 1 |
| `FLASK_RUN_HOST` | Host to bind the server | No | 127.0.0.1 |
| `FLASK_RUN_PORT` | Port to bind the server | No | 5000 |
| `SECRET_KEY` | Flask secret key for sessions | No | Auto-generated |

*Not required to run, but features will be limited without them.

### Email Setup (Gmail)

1. Go to your Google Account settings
2. Enable **2-Step Verification**
3. Generate an **App Password**:
   - Go to Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password
4. Use this App Password in your `.env` file

---

## Usage

### User Features

1. **Sign Up / Login**
   - Create an account with email verification
   - Login with existing credentials

2. **Browse Monuments**
   - Explore UNESCO heritage sites
   - View details, images, and locations on map

3. **Book Tickets**
   - Select monument, date, and number of visitors
   - Choose tour guide (optional)
   - Receive confirmation via email/WhatsApp

4. **Hire Tour Guides**
   - Browse verified tour guides
   - View guide profiles, ratings, and specializations
   - Book tour packages

5. **Shop Merchandise**
   - Browse clothing, accessories, and souvenirs
   - Add items to cart and checkout
   - Track order history

6. **Write Reviews**
   - Share your experiences
   - Rate monuments and guides
   - Upload photos

7. **Earn Itihaas Coins**
   - Earn coins through bookings and activities
   - Use coins for discounts on future bookings

### Guide Features

1. **Register as Guide**
   - Sign up with guide credentials
   - Add experience, languages, and specializations
   - Get verified by admin

2. **Create Tour Packages**
   - Design custom tour packages
   - Set pricing and duration
   - Manage bookings

3. **View Dashboard**
   - Track bookings and earnings
   - Manage availability
   - View ratings and reviews

### Admin Features

- Manage users, guides, and bookings
- Verify tour guides
- Monitor transactions
- Manage merchandise inventory

---

## API Endpoints

### Authentication
- `POST /sign-up` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /verify-email` - Email verification

### Bookings
- `GET /booking` - Booking form
- `POST /booking` - Create booking
- `GET /booking-history` - View booking history

### Merchandise
- `GET /shop` - Browse products
- `GET /shop/<id>` - Product details
- `POST /cart/add` - Add to cart
- `GET /cart` - View cart
- `POST /checkout` - Checkout

### Chatbot
- `POST /chatbot/chat` - Send message to chatbot
- `GET /chatbot/get_monuments` - Get monument list

---

## Database Models

- **User** - User accounts and authentication
- **Booking** - Monument visit bookings
- **Guide** - Tour guide profiles
- **TourPackage** - Guided tour packages
- **Merchandise** - Shop products
- **Order** - Purchase orders
- **Review** - User reviews and ratings
- **ItihaasCoins** - Loyalty points system
- **Transaction** - Payment transactions

---

## Troubleshooting

### Email not sending

**Error**: "Error sending verification email. Please try again."

**Solution**:
1. Check that `EMAIL_USER` and `EMAIL_PASSWORD` are set in `.env`
2. Ensure you're using a Gmail App Password, not your regular password
3. Check `email.log` for detailed error messages
4. Verify 2-Step Verification is enabled on your Google Account

### Import errors

**Error**: `ModuleNotFoundError: No module named 'Itihaas'`

**Solution**:
- Run `python run.py` from the project root directory
- Or set `PYTHONPATH=/workspaces` before running

### Database errors

**Error**: Database tables not found

**Solution**:
1. Delete `instance/database.db`
2. Restart the app to recreate tables
3. Or run Flask-Migrate commands:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

### Google Maps not loading

**Solution**:
1. Set `GOOGLE_MAPS_API_KEY` in `.env`
2. Enable Maps JavaScript API in Google Cloud Console
3. Check browser console for API errors

---

## Development

### Running Tests

```bash
# Coming soon
python -m pytest
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Adding New Features

1. Create new routes in `views.py` or create a new blueprint
2. Add database models in `models.py`
3. Create templates in `templates/`
4. Update this README with new features

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is part of the Colloquium 2025 IT for Society initiative.

---

## Acknowledgments

- Built for **Colloquium 2025** - IT for Society Project
- UNESCO World Heritage Sites data
- Indian tourism and cultural heritage promotion

---

## Contact

For questions or support, please open an issue on GitHub.

---

## Future Enhancements

- [ ] Payment gateway integration (Stripe/Razorpay)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Social media integration
- [ ] AR/VR monument tours
- [ ] Multi-currency support
- [ ] Advanced search and filters
- [ ] Blog/news section
- [ ] Push notifications
- [ ] Offline mode support 

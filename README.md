<img width="1901" height="902" alt="image" src="https://github.com/user-attachments/assets/a7210c68-6d18-4550-a6c7-e2ffa32c2232" />Itihaas - Indian Heritage Tourism Platform
image
🌟 Overview
image
Itihaas is a comprehensive Indian heritage tourism platform that connects travelers with India's rich cultural heritage, monuments, and historical sites. The platform offers guided tours, merchandise, interactive maps, and a unique reward system to enhance the tourism experience.

🏛️ Features
<img width="1901" height="902" alt="Screenshot_2025-09-21_212421" src="https://github.com/user-attachments/assets/b682acfe-9c24-4eeb-b1c9-53d11498ffde" />

<img width="1906" height="904" alt="Screenshot_2025-09-21_212427" src="https://github.com/user-attachments/assets/e2cd1d48-3fe1-4f33-9d1a-c3d28ecbed3e" />
<img width="1907" height="910" alt="Screenshot_2025-09-21_212439" src="https://github.com/user-attachments/assets/022d0280-7043-4755-bdf4-418df28f266e" />
<img width="1913" height="906" alt="Screenshot_2025-09-21_212500" src="https://github.com/user-attachments/assets/b96a7ab8-45fd-46b6-a8b2-17f1aef6da3d" />
<img wid<img width="1915" height="903" alt="Screenshot_2025-09-21_212510" src="https://github.com/user-attachments/assets/c43e8d21-22eb-469c-884d-4bb9ccc5a2e9" />
th="1919" height="913" alt="Screenshot_2025-09-21_212505" src="https://github.com/user-attachments/assets/f4e3d35d-9845-4434-9f7a-f2d7871fda97" />

Core Features
Interactive Heritage Map: Explore UNESCO World Heritage sites and monuments across India
Guided Tours: Connect with certified tour guides for personalized experiences
Booking System: Reserve visits to monuments and heritage sites
Multilingual Support: Available in English and Hindi
User Reviews & Ratings: Share experiences and read reviews from other travelers
News Integration: Stay updated with latest heritage and tourism news
E-commerce Features
Heritage Merchandise: Shop for traditional Indian clothing and souvenirs
Shopping Cart: Add items and manage your shopping experience
Order Management: Track orders and view order history
Payment Integration: Secure payment processing
User Management
User Registration & Authentication: Secure login system with email verification
Profile Management: Upload profile pictures and manage personal information
Guide Registration: Special registration for tour guides
Admin Dashboard: Comprehensive admin panel for platform management
Interactive Features
AI Chatbot: Get instant assistance and information about heritage sites
WhatsApp Integration: Receive booking confirmations via WhatsApp
Automated Messaging: Scheduled notifications and updates
Itihaas Coins: Reward system for user engagement and activities
Content Features
Festival Calendar: Discover festivals and celebrations across India
Video Content: Educational videos about heritage sites
Photo Galleries: Visual exploration of monuments and sites
Audio Narration: Guided audio tours for monuments
🛠️ Technology Stack
Backend
Flask: Python web framework
SQLAlchemy: Database ORM
Flask-Login: User authentication
Flask-WTF: Form handling and CSRF protection
Flask-Babel: Internationalization support
Frontend
HTML5/CSS3: Modern responsive design
JavaScript: Interactive user experience
Bootstrap: UI framework for responsive layouts
External APIs
Google Maps API: Interactive mapping and location services
GNews API: Real-time news integration
WhatsApp Business API: Messaging integration
Database
SQLite: Development database
SQLAlchemy: Database management and migrations
📦 Installation
Prerequisites
Python 3.8 or higher
pip (Python package manager)
Git
Setup Instructions
Clone the repository

git clone <repository-url>
cd itihaas
Navigate to the project directory

cd project
Create a virtual environment

python -m venv venv
Activate the virtual environment

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
Install dependencies

pip install -r requirements.txt
Set up environment variables Create a .env file in the project directory with the following variables:

FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
GNEWS_API_KEY=your-gnews-api-key
Initialize the database

python main.py
Run the application

flask run
The application will be available at http://localhost:5000

🗂️ Project Structure
itihaas/
├── project/
│   ├── main.py                 # Application entry point
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── models.py             # Database models
│   └── website/
│       ├── __init__.py       # Flask app factory
│       ├── views.py          # Main route handlers
│       ├── auth.py           # Authentication routes
│       ├── merchandise.py    # E-commerce functionality
│       ├── chatbot.py        # AI chatbot integration
│       ├── whatsapp.py       # WhatsApp messaging
│       ├── automated_messaging.py  # Automated notifications
│       ├── models.py         # Database models
│       ├── merchandise_models.py   # E-commerce models
│       ├── static/           # Static files (CSS, JS, images)
│       └── templates/        # HTML templates
└── README.md
🚀 Key Features Explained
Interactive Map
Explore heritage sites across India
Filter by categories (temples, forts, palaces, etc.)
Get detailed information about each site
View location coordinates and directions
Booking System
Reserve visits to monuments
Select preferred dates and times
Choose number of visitors
Receive confirmation via email and WhatsApp
Guide Management
Certified guides can register on the platform
Users can browse and book guides
Guide profiles with experience and specializations
Rating and review system for guides
Merchandise Shop
Traditional Indian clothing and accessories
Secure shopping cart functionality
Order tracking and history
Multiple payment options
Itihaas Coins
Earn coins for various activities
Redeem coins for discounts and rewards
Track coin balance and transaction history
🔧 Configuration
Environment Variables
SECRET_KEY: Flask secret key for session management
EMAIL_USER: Gmail address for sending emails
EMAIL_PASSWORD: Gmail app password
GOOGLE_MAPS_API_KEY: Google Maps API key
GNEWS_API_KEY: GNews API key for news integration
Database Configuration
The application uses SQLite by default for development. For production, you can configure other databases like PostgreSQL or MySQL.

📱 API Endpoints
Authentication
POST /sign-up: User registration
POST /login: User login
POST /logout: User logout
POST /verify-email: Email verification
Tours & Bookings
GET /index: Heritage sites listing
POST /book: Create new booking
GET /booking-history: View booking history
POST /guide-signup: Guide registration
Merchandise
GET /shop: Product catalog
GET /product/<id>: Product details
POST /add-to-cart: Add to shopping cart
POST /checkout: Process order
Reviews & Ratings
GET /review: View all reviews
POST /api/reviews: Submit new review
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Team
CEO: Project leadership and strategy
CTO: Technical architecture and development
CRO: Revenue optimization and business development
Curator: Content management and heritage expertise
📞 Support
For support and queries:

Email: itihaasdairy@gmail.com
Website: Itihaas Platform
🔮 Future Enhancements
Mobile app development
Virtual reality tours
Advanced AI recommendations
Social media integration
Multi-language support expansion
Advanced analytics dashboard
Itihaas - Preserving India's Heritage, One Journey at a Time 🇮🇳

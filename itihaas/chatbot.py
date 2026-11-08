from flask import Blueprint, render_template_string, jsonify, request

# Create a blueprint for the chatbot
chatbot_bp = Blueprint('chatbot', __name__)

def show_monument_info(monument):
    return f'''
        <div class="info-section">
            <h4>{monument["name"]}</h4>
            <p><strong>Location:</strong> {monument["location"]}</p>
            <p><strong>Description:</strong> {monument["description"]}</p>
            <p><strong>Timings:</strong> {monument["timings"]}</p>
            <p><strong>Entry Fee:</strong></p>
            <ul>
                <li>Indian: {monument["entry_fee"]["indian"]}</li>
                <li>Foreigner: {monument["entry_fee"]["foreigner"]}</li>
                <li>Children under 15: {monument["entry_fee"]["children_under_15"]}</li>
            </ul>
            <p><strong>Best Time to Visit:</strong> {monument["best_time_to_visit"]}</p>
            <p><strong>Transportation:</strong></p>
            <ul>
                <li>Nearest Airport: {monument["transportation"]["nearest_airport"]}</li>
                <li>Nearest Railway: {monument["transportation"]["nearest_railway"]}</li>
                <li>Local Transport: {monument["transportation"]["local_transport"]}</li>
            </ul>
            <p><strong>Nearby Hotels:</strong></p>
            <ul>
                {"".join([f"<li>{hotel}</li>" for hotel in monument["nearby_hotels"]])}
            </ul>
            <p><strong>Food Options:</strong></p>
            <ul>
                {"".join([f"<li>{food}</li>" for food in monument["food_options"]])}
            </ul>
            <p><strong>Shopping Places:</strong></p>
            <ul>
                {"".join([f"<li>{shop}</li>" for shop in monument["shopping_places"]])}
            </ul>
        </div>
    '''

# Monument information dictionary
MONUMENTS = {
    "taj_mahal": {
        "name": "Taj Mahal",
        "location": "Agra, Uttar Pradesh",
        "description": "A white marble mausoleum built by Emperor Shah Jahan in memory of his wife Mumtaz Mahal.",
        "timings": "Sunrise to sunset (closed on Fridays)",
        "entry_fee": {
            "indian": "₹50",
            "foreigner": "₹1100",
            "children_under_15": "Free"
        },
        "food_options": [
            "Pinch of Spice - North Indian cuisine",
            "Peshawri - Authentic Mughlai cuisine",
            "Dasaprakash - South Indian vegetarian food",
            "Cafeteria Taj Mahal - Quick bites inside the complex"
        ],
        "nearby_hotels": [
            "The Oberoi Amarvilas - 5-star luxury with Taj Mahal views",
            "Radisson Hotel Agra - 4-star hotel with rooftop pool",
            "Hotel Taj Resort - Budget-friendly option close to the monument",
            "Trident Agra - Premium luxury hotel"
        ],
        "nearby_monuments": [
            "Agra Fort (6 km)",
            "Fatehpur Sikri (43 km)",
            "Itmad-ud-Daulah's Tomb (8 km)",
            "Mehtab Bagh (1 km)"
        ],
        "shopping_places": [
            "Taj Mahal Complex Shops - Handicrafts and souvenirs",
            "Sadar Bazaar - Traditional markets",
            "TDI Mall - Modern shopping complex",
            "Pacific Mall Agra - Premium shopping experience"
        ],
        "transportation": {
            "nearest_airport": "Agra Airport (12 km)",
            "nearest_railway": "Agra Cantt Railway Station (6 km)",
            "bus_stands": "ISBT Agra (8 km)",
            "local_transport": "Auto-rickshaws, cycle-rickshaws, and e-rickshaws available"
        },
        "best_time_to_visit": "October to March"
    },
    "red_fort": {
        "name": "Red Fort",
        "location": "Delhi",
        "description": "A historic fort that served as the main residence of Mughal emperors for nearly 200 years.",
        "timings": "9:30 AM to 4:30 PM (closed on Mondays)",
        "entry_fee": {
            "indian": "₹35",
            "foreigner": "₹550",
            "children_under_15": "Free"
        },
        "food_options": [
            "Karim's - Famous for Mughlai cuisine",
            "Moti Mahal - Known for butter chicken",
            "Paranthe Wali Gali - Variety of stuffed parathas",
            "Haldiram's - Vegetarian North Indian snacks"
        ],
        "nearby_hotels": [
            "The LaLiT New Delhi - Luxury hotel with modern amenities",
            "Maidens Hotel - Heritage hotel with colonial charm",
            "Hotel Tara Palace - Budget-friendly option near Chandni Chowk",
            "Hotel Broadway - Mid-range hotel with vintage decor"
        ],
        "nearby_monuments": [
            "Jama Masjid (1 km)",
            "Raj Ghat (3 km)",
            "India Gate (6 km)",
            "Qutub Minar (15 km)"
        ],
        "shopping_places": [
            "Chandni Chowk - Traditional market for textiles and jewelry",
            "Connaught Place - Modern shopping and dining hub",
            "Dilli Haat - Handicrafts and street food from various states",
            "Palika Bazaar - Underground market for electronics and clothing"
        ],
        "transportation": {
            "nearest_airport": "Indira Gandhi International Airport (20 km)",
            "nearest_railway": "New Delhi Railway Station (3 km)",
            "bus_stands": "Kashmere Gate ISBT (5 km)",
            "local_transport": "Metro, auto-rickshaws, cycle-rickshaws, and taxis available"
        },
        "best_time_to_visit": "October to March"
    },
    "qutub_minar": {
        "name": "Qutub Minar",
        "location": "Delhi",
        "description": "A UNESCO World Heritage Site, this 73-meter tall minaret is a fine example of Indo-Islamic architecture.",
        "timings": "Sunrise to sunset",
        "entry_fee": {
            "indian": "₹30",
            "foreigner": "₹500",
            "children_under_15": "Free"
        },
        "food_options": [
            "Olive Bar & Kitchen - Mediterranean cuisine in a rustic setting",
            "Lavaash by Saby - Armenian cuisine with a Bengali twist",
            "Qla - European cuisine with live music",
            "Raasta - Caribbean lounge with eclectic menu"
        ],
        "nearby_hotels": [
            "The Claridges - Luxury hotel with classic decor",
            "Eros Hotel - 5-star hotel with modern amenities",
            "Hotel Saket 27 - Mid-range option near Saket",
            "FabHotel Anutham Saket - Budget-friendly accommodation"
        ],
        "nearby_monuments": [
            "Iron Pillar (0.1 km)",
            "Lotus Temple (10 km)",
            "Humayun's Tomb (12 km)",
            "India Gate (14 km)"
        ],
        "shopping_places": [
            "Select Citywalk - Upscale mall with international brands",
            "DLF Place Saket - Shopping and entertainment complex",
            "Hauz Khas Village - Boutiques and art galleries",
            "Sarojini Nagar Market - Popular for affordable fashion"
        ],
        "transportation": {
            "nearest_airport": "Indira Gandhi International Airport (15 km)",
            "nearest_railway": "Hazrat Nizamuddin Railway Station (10 km)",
            "bus_stands": "Saket Bus Stand (3 km)",
            "local_transport": "Metro, auto-rickshaws, and taxis available"
        },
        "best_time_to_visit": "October to March"
    },
    "gateway_of_india": {
        "name": "Gateway of India",
        "location": "Mumbai, Maharashtra",
        "description": "An iconic arch-monument built during the 20th century in Mumbai, overlooking the Arabian Sea.",
        "timings": "Open 24 hours",
        "entry_fee": {
            "indian": "Free",
            "foreigner": "Free",
            "children_under_15": "Free"
        },
        "food_options": [
            "Leopold Cafe - Historic cafe known for its eclectic menu",
            "Bademiya - Famous for kebabs and rolls",
            "Cafe Mondegar - Vibrant cafe with continental dishes",
            "The Table - Modern European cuisine"
        ],
        "nearby_hotels": [
            "The Taj Mahal Palace - Luxury hotel with historic significance",
            "Trident Nariman Point - 5-star hotel with sea views",
            "Fariyas Hotel - Mid-range option with modern amenities",
            "Hotel Suba Palace - Budget-friendly accommodation"
        ],
        "nearby_monuments": [
            "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (1 km)",
            "Chhatrapati Shivaji Terminus (3 km)",
            "Marine Drive (2 km)",
            "Elephanta Caves (Ferry from Gateway)"
        ],
        "shopping_places": [
            "Colaba Causeway - Street shopping for fashion and accessories",
            "Fashion Street - Affordable clothing market",
            "Crawford Market - Fresh produce and spices",
            "High Street Phoenix - Upscale mall with branded stores"
        ],
        "transportation": {
            "nearest_airport": "Chhatrapati Shivaji Maharaj International Airport (25 km)",
            "nearest_railway": "Chhatrapati Shivaji Terminus (3 km)",
            "bus_stands": "Mumbai Central Bus Depot (7 km)",
            "local_transport": "Local trains, buses, taxis, and auto-rickshaws available"
        },
        "best_time_to_visit": "November to February"
    },
    "hawa_mahal": {
        "name": "Hawa Mahal",
        "location": "Jaipur, Rajasthan",
        "description": "Known as the 'Palace of Winds,' this pink sandstone structure features 953 small windows and was built for royal women to observe street festivals.",
        "timings": "9:00 AM to 4:30 PM",
        "entry_fee": {
            "indian": "₹50",
            "foreigner": "₹200",
            "children_under_15": "Free"
        },
        "food_options": [
            "Laxmi Misthan Bhandar - Traditional Rajasthani sweets and snacks",
            "The Tattoo Cafe - Rooftop cafe with Hawa Mahal views",
            "Wind View Cafe - Light bites with panoramic views",
            "Hawk View Restaurant - Multi-cuisine dishes with city vistas"
        ],
        "nearby_hotels": [
            "The Oberoi Rajvilas - Luxury resort with royal ambiance",
            "Trident Jaipur - 5-star hotel overlooking Mansagar Lake",
            "Hotel Pearl Palace - Budget-friendly heritage stay",
            "Alsisar Haveli - A heritage hotel with Rajput-style decor"
        ],
        "nearby_monuments": [
            "City Palace (1 km)",
            "Jantar Mantar (1 km)",
            "Amber Fort (11 km)",
            "Nahargarh Fort (5 km)"
        ],
        "shopping_places": [
            "Johari Bazaar - Famous for gemstones and jewelry",
            "Bapu Bazaar - Popular for textiles and handicrafts",
            "Tripolia Bazaar - Known for lac jewelry and brassware",
            "Nehru Bazaar - Footwear and local souvenirs"
        ],
        "transportation": {
            "nearest_airport": "Jaipur International Airport (13 km)",
            "nearest_railway": "Jaipur Junction Railway Station (5 km)",
            "bus_stands": "Sindhi Camp Bus Stand (4 km)",
            "local_transport": "Auto-rickshaws, cycle-rickshaws, taxis, and app-based cabs available"
        },
        "best_time_to_visit": "October to March"
    },
    "india_gate": {
        "name": "India Gate",
        "location": "New Delhi",
        "description": "A war memorial built in honor of Indian soldiers who died in World War I.",
        "timings": "Open 24 hours",
        "entry_fee": {
            "indian": "Free",
            "foreigner": "Free",
            "children_under_15": "Free"
        },
        "food_options": [
            "Kwality Restaurant - Famous for North Indian cuisine",
            "The Imperial Spice - Fine dining experience",
            "Andhra Bhavan - Authentic South Indian meals",
            "Bikanervala - Vegetarian snacks and sweets"
        ],
        "nearby_hotels": [
            "The Taj Mahal Hotel - Luxury hotel near India Gate",
            "The Oberoi New Delhi - 5-star hotel with city views",
            "Hotel The Royal Plaza - Mid-range option",
            "The Janpath Hotel - Budget-friendly accommodation"
        ],
        "nearby_monuments": [
            "Rashtrapati Bhavan (2 km)",
            "National War Memorial (0.5 km)",
            "Jantar Mantar (3 km)",
            "Humayun's Tomb (5 km)"
        ],
        "shopping_places": [
            "Connaught Place - Popular shopping hub",
            "Janpath Market - Handicrafts and souvenirs",
            "Pallika Bazaar - Underground market for clothes and electronics",
            "Khan Market - High-end boutique shopping"
        ],
        "transportation": {
            "nearest_airport": "Indira Gandhi International Airport (15 km)",
            "nearest_railway": "New Delhi Railway Station (4 km)",
            "bus_stands": "Kashmere Gate ISBT (7 km)",
            "local_transport": "Metro, taxis, auto-rickshaws, and buses available"
        },
        "best_time_to_visit": "October to March"
    },
    "charminar": {
        "name": "Charminar",
        "location": "Hyderabad, Telangana",
        "description": "A grand monument with four minarets, built in 1591, known for its Indo-Islamic architecture.",
        "timings": "9:30 AM to 5:30 PM",
        "entry_fee": {
            "indian": "₹25",
            "foreigner": "₹300",
            "children_under_15": "Free"
        },
        "food_options": [
            "Hotel Shadab - Famous for Hyderabadi biryani",
            "Pista House - Authentic Haleem and sweets",
            "Nimrah Cafe - Popular for Irani chai and Osmania biscuits",
            "Shah Ghouse - Well-known for kebabs and biryani"
        ],
        "nearby_hotels": [
            "Taj Falaknuma Palace - Luxurious heritage hotel",
            "The Park Hyderabad - 5-star hotel with lake views",
            "Hotel Shree Venkateshwara - Budget-friendly option",
            "FabHotel Deccan Heritage - Mid-range accommodation"
        ],
        "nearby_monuments": [
            "Mecca Masjid (0.5 km)",
            "Golconda Fort (11 km)",
            "Qutb Shahi Tombs (9 km)",
            "Chowmahalla Palace (1 km)"
        ],
        "shopping_places": [
            "Laad Bazaar - Famous for bangles and pearls",
            "Sultan Bazaar - Traditional shopping street",
            "Begum Bazaar - Wholesale shopping market",
            "GVK One Mall - High-end shopping complex"
        ],
        "transportation": {
            "nearest_airport": "Rajiv Gandhi International Airport (20 km)",
            "nearest_railway": "Hyderabad Deccan Railway Station (5 km)",
            "bus_stands": "Mahatma Gandhi Bus Station (4 km)",
            "local_transport": "Auto-rickshaws, taxis, and metro available"
        },
        "best_time_to_visit": "November to February"
    },
    "sun_temple_konark": {
        "name": "Sun Temple",
        "location": "Konark, Odisha",
        "description": "A 13th-century temple dedicated to the Sun God, known for its intricate stone carvings.",
        "timings": "6:00 AM to 8:00 PM",
        "entry_fee": {
            "indian": "₹40",
            "foreigner": "₹600",
            "children_under_15": "Free"
        },
        "food_options": [
            "Eco Retreat Konark - Luxury dining experience",
            "Chandralok Restaurant - Local Odia cuisine",
            "Sun Temple Hotel - Traditional vegetarian meals",
            "Konark Highway Inn - North and South Indian dishes"
        ],
        "nearby_hotels": [
            "Lotus Eco Resort - Beachfront luxury stay",
            "Toshali Sands Resort - Premium resort with Ayurvedic spa",
            "Konark Lodge - Budget accommodation",
            "Yatri Nivas - Government-run tourist guest house"
        ],
        "nearby_monuments": [
            "Ramachandi Temple (7 km)",
            "Chandrabhaga Beach (3 km)",
            "Jagannath Temple Puri (35 km)",
            "Lingaraj Temple Bhubaneswar (65 km)"
        ],
        "shopping_places": [
            "Konark Handicrafts Market - Local stone and wood carvings",
            "Pipili Applique Market - Famous for applique work",
            "Grand Road Puri - Traditional markets",
            "Ekamra Haat Bhubaneswar - Authentic Odisha handicrafts"
        ],
        "transportation": {
            "nearest_airport": "Biju Patnaik International Airport (64 km)",
            "nearest_railway": "Puri Railway Station (35 km)",
            "bus_stands": "Konark Bus Stand (2 km)",
            "local_transport": "Taxis and auto-rickshaws available"
        },
        "best_time_to_visit": "November to February"
    },
    "mysore_palace": {
        "name": "Mysore Palace",
        "location": "Mysore, Karnataka",
        "description": "A grand royal palace that was the residence of the Wadiyar dynasty, known for its Indo-Saracenic architecture.",
        "timings": "10:00 AM to 5:30 PM",
        "entry_fee": {
            "indian": "₹100",
            "foreigner": "₹400",
            "children_under_15": "₹50"
        },
        "food_options": [
            "Vinayaka Mylari - Famous for soft dosas",
            "The Old House - Italian and Indian cuisine",
            "Rrr - Authentic Karnataka-style meals",
            "La Uppu - Luxury dining with South Indian flavors"
        ],
        "nearby_hotels": [
            "Radisson Blu Plaza Hotel - 5-star luxury stay",
            "Royal Orchid Metropole - Heritage hotel",
            "Hotel Pai Vista - Mid-range accommodation",
            "Treebo Trend Akshaya Mahal - Budget-friendly stay"
        ],
        "nearby_monuments": [
            "Chamundi Hill Temple (13 km)",
            "Brindavan Gardens (20 km)",
            "St. Philomena's Church (3 km)",
            "Jaganmohan Palace (1 km)"
        ],
        "shopping_places": [
            "Devaraja Market - Famous for silk sarees and spices",
            "Mall of Mysore - High-end shopping",
            "Cauvery Emporium - Authentic Mysore handicrafts",
            "Forum Centre City Mall - Modern shopping experience"
        ],
        "transportation": {
            "nearest_airport": "Mysore Airport (12 km)",
            "nearest_railway": "Mysore Junction Railway Station (2 km)",
            "bus_stands": "Mysore KSRTC Bus Stand (1 km)",
            "local_transport": "Auto-rickshaws, taxis, and city buses available"
        },
        "best_time_to_visit": "October to February"
    },
    "golden_temple": {
        "name": "Golden Temple",
        "location": "Amritsar, Punjab",
        "description": "The holiest shrine of Sikhism, known for its stunning golden architecture and the sacred Amrit Sarovar.",
        "timings": "Open 24 hours",
        "entry_fee": {
            "indian": "Free",
            "foreigner": "Free",
            "children_under_15": "Free"
        },
        "food_options": [
            "Guru Ka Langar - Free community kitchen",
            "Kesar Da Dhaba - Famous for dal makhani",
            "Bharawan Da Dhaba - Traditional Punjabi cuisine",
            "Crystal Restaurant - Multi-cuisine dining"
        ],
        "nearby_hotels": [
            "Hotel Golden Tower - Luxury stay with temple views",
            "Hotel City Heart - Mid-range accommodation",
            "Hotel Ritz Plaza - Budget-friendly option",
            "Hotel Le Golden - Premium hotel near temple"
        ],
        "nearby_monuments": [
            "Jallianwala Bagh (1 km)",
            "Partition Museum (2 km)",
            "Durgiana Temple (3 km)",
            "Wagah Border (28 km)"
        ],
        "shopping_places": [
            "Hall Bazaar - Traditional market",
            "Katra Jaimal Singh - Famous for phulkari work",
            "Lawrence Road - Modern shopping area",
            "Mall Road - Premium shopping complex"
        ],
        "transportation": {
            "nearest_airport": "Sri Guru Ram Dass Jee International Airport (11 km)",
            "nearest_railway": "Amritsar Junction (2 km)",
            "bus_stands": "ISBT Amritsar (3 km)",
            "local_transport": "Auto-rickshaws, cycle-rickshaws, and taxis available"
        },
        "best_time_to_visit": "October to March"
    },
    "mehrangarh_fort": {
        "name": "Mehrangarh Fort",
        "location": "Jodhpur, Rajasthan",
        "description": "One of India's largest forts, perched on a rocky hill, offering panoramic views of the Blue City.",
        "timings": "9:00 AM to 5:00 PM",
        "entry_fee": {
            "indian": "₹100",
            "foreigner": "₹600",
            "children_under_15": "₹50"
        },
        "food_options": [
            "Chokelao Garden Restaurant - Rooftop dining with fort views",
            "Indique - Multi-cuisine restaurant",
            "Jhankar Choti Haveli - Traditional Rajasthani food",
            "Cafe Sheesh Mahal - Light bites and coffee"
        ],
        "nearby_hotels": [
            "Taj Umaid Bhawan Palace - Luxury heritage hotel",
            "WelcomHeritage Mandore - Heritage property",
            "Hotel Haveli - Mid-range accommodation",
            "Hotel Padmini - Budget-friendly stay"
        ],
        "nearby_monuments": [
            "Jaswant Thada (1 km)",
            "Umaid Bhawan Palace (3 km)",
            "Mandore Gardens (8 km)",
            "Balsamand Lake (5 km)"
        ],
        "shopping_places": [
            "Sardar Market - Traditional bazaar",
            "Nai Sarak - Textiles and handicrafts",
            "Sojati Gate Market - Local specialties",
            "Mochi Bazaar - Famous for juttis"
        ],
        "transportation": {
            "nearest_airport": "Jodhpur Airport (5 km)",
            "nearest_railway": "Jodhpur Junction (3 km)",
            "bus_stands": "Rawatbhata Bus Stand (2 km)",
            "local_transport": "Auto-rickshaws, taxis, and cycle-rickshaws available"
        },
        "best_time_to_visit": "October to March"
    },
    "ajanta_caves": {
        "name": "Ajanta Caves",
        "location": "Aurangabad, Maharashtra",
        "description": "Ancient Buddhist rock-cut caves featuring exquisite paintings and sculptures.",
        "timings": "9:00 AM to 5:00 PM (closed on Mondays)",
        "entry_fee": {
            "indian": "₹40",
            "foreigner": "₹600",
            "children_under_15": "Free"
        },
        "food_options": [
            "MTDC Restaurant - Government-run restaurant",
            "Green Leaf Restaurant - Local cuisine",
            "Hotel Kailas - Multi-cuisine dining",
            "Cafe Coffee Day - Quick bites"
        ],
        "nearby_hotels": [
            "Hotel Ajanta Ambassador - Luxury stay",
            "Hotel Kailas - Mid-range accommodation",
            "MTDC Holiday Resort - Government-run hotel",
            "Hotel Panchavati - Budget-friendly option"
        ],
        "nearby_monuments": [
            "Ellora Caves (100 km)",
            "Bibi Ka Maqbara (30 km)",
            "Daulatabad Fort (15 km)",
            "Grishneshwar Temple (30 km)"
        ],
        "shopping_places": [
            "Paithan Market - Traditional textiles",
            "Aurangabad Main Market - Local handicrafts",
            "Prozone Mall - Modern shopping",
            "Gulmandi Market - Traditional bazaar"
        ],
        "transportation": {
            "nearest_airport": "Aurangabad Airport (60 km)",
            "nearest_railway": "Jalgaon Junction (60 km)",
            "bus_stands": "Aurangabad Bus Stand (100 km)",
            "local_transport": "Taxis and buses available"
        },
        "best_time_to_visit": "October to March"
    }
}

# HTML template for the floating chatbot widget
chatbot_widget = '''
<div id="chatbot-widget">
    <div id="chatbot-header" onclick="toggleChat()">
        <span>Monuments Assistant</span>
        <i class="fas fa-chevron-up" id="chat-toggle-icon"></i>
    </div>
    <div id="chatbot-body" style="display: none;">
        <div id="search-section">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="Search monuments or locations...">
                <button onclick="performSearch()">
                    <i class="fas fa-search"></i>
                </button>
            </div>
        </div>
        <div id="monument-selector">
            <label for="monument-dropdown">Select a Monument:</label>
            <select id="monument-dropdown" onchange="selectMonumentFromDropdown(this.value)">
                <option value="">Choose a monument...</option>
            </select>
        </div>
        <div id="chatbox"></div>
        <div id="info-tabs" style="display: none;">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="showTab('overview')">Overview</button>
                <button class="tab-button" onclick="showTab('transport')">Transport</button>
                <button class="tab-button" onclick="showTab('food')">Food & Hotels</button>
                <button class="tab-button" onclick="showTab('shopping')">Shopping</button>
            </div>
            <div id="overview-tab" class="tab-content active"></div>
            <div id="transport-tab" class="tab-content"></div>
            <div id="food-tab" class="tab-content"></div>
            <div id="shopping-tab" class="tab-content"></div>
        </div>
        <div id="chatbot-options">
            <button onclick="sendOption('list_monuments')">List Monuments</button>
            <button onclick="sendOption('book_ticket')">Book Ticket</button>
            <button onclick="sendOption('view_info')">View Info</button>
            <button onclick="sendOption('cancel_ticket')">Cancel Ticket</button>
            <button onclick="sendOption('nearby_attractions')">Nearby Attractions</button>
            <button onclick="sendOption('help')">Help</button>
        </div>
        <div id="prompt-box">
            <input type="text" id="user-input" placeholder="Type your question here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendUserMessage()" id="send-button">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>
</div>

<style>
    #chatbot-widget {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 350px;
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        overflow: hidden;
        z-index: 1000;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
    }

    @media (max-width: 480px) {
        #chatbot-widget {
            width: 290px;
            left: 10px;
            bottom: 10px;
        }
        
        #chatbot-options {
            grid-template-columns: 1fr;
        }
        
        .tab-buttons {
            gap: 3px;
        }
        
        .tab-button {
            padding: 6px 4px;
            font-size: 12px;
            min-width: 60px;
        }
    }

    #monument-selector {
        padding: 15px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin-bottom: 10px;
    }

    #monument-selector label {
        display: block;
        color: white;
        margin-bottom: 8px;
        font-weight: 500;
    }

    #monument-dropdown {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #f1683a;
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    #monument-dropdown:hover {
        border-color: #e65100;
        background: white;
    }

    #monument-dropdown:focus {
        outline: none;
        border-color: #e65100;
        box-shadow: 0 0 5px rgba(241, 104, 58, 0.5);
    }

    #monument-dropdown option {
        padding: 8px;
        background: white;
        color: #333;
    }

    #monument-dropdown option:first-child {
        color: #666;
        font-style: italic;
    }

    #info-tabs {
        margin: 10px 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding: 10px;
        display: block;
    }

    .tab-buttons {
        display: flex;
        gap: 5px;
        margin-bottom: 10px;
        flex-wrap: wrap;
    }

    .tab-button {
        flex: 1;
        padding: 8px;
        border: none;
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        cursor: pointer;
        transition: background 0.3s ease;
        min-width: 80px;
    }

    .tab-button.active {
        background: #f1683a;
    }

    .tab-content {
        display: none;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin-top: 10px;
    }

    .tab-content.active {
        display: block !important;
    }

    #chatbot-header {
        background: #f1683a;
        color: white;
        padding: 10px 15px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 500;
    }

    #chat-toggle-icon {
        transition: transform 0.3s ease;
    }

    #chatbot-body {
        padding: 15px;
    }

    #chatbox {
        height: 150px;
        overflow-y: auto;
        margin-bottom: 10px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
    }

    #chatbox::-webkit-scrollbar {
        width: 5px;
    }

    #chatbox::-webkit-scrollbar-thumb {
        background-color: rgba(241, 104, 58, 0.5);
        border-radius: 5px;
    }

    #chatbox::-webkit-scrollbar-track {
        background-color: rgba(255, 255, 255, 0.1);
    }

    .message {
        margin: 5px 0;
        padding: 8px 12px;
        border-radius: 15px;
        max-width: 80%;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user {
        background: #f1683a;
        color: white;
        margin-left: auto;
        border-radius: 15px 15px 0 15px;
    }

    .bot {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        margin-right: auto;
        border-radius: 15px 15px 15px 0;
    }

    #chatbot-options {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 5px;
    }

    #chatbot-options button {
        padding: 8px;
        border: none;
        border-radius: 5px;
        background: #f1683a;
        color: white;
        cursor: pointer;
        transition: background 0.3s ease;
    }

    #chatbot-options button:hover {
        background: #e65100;
    }

    .monument-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .monument-list li {
        padding: 5px 0;
        cursor: pointer;
        color: #f1683a;
    }

    .monument-list li:hover {
        text-decoration: underline;
    }

    .info-section {
        margin: 10px 0;
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }

    .info-section h4 {
        color: #f1683a;
        margin: 5px 0;
        font-size: 16px;
    }

    .info-section p {
        margin: 8px 0;
        color: white;
    }

    .info-section ul {
        list-style: none;
        padding-left: 15px;
        margin: 8px 0;
    }

    .info-section li {
        margin: 5px 0;
        color: white;
        line-height: 1.4;
    }

    #prompt-box {
        display: flex;
        gap: 10px;
        margin-top: 10px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
    }

    #user-input {
        flex: 1;
        padding: 10px;
        border: 2px solid #f1683a;
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        font-size: 14px;
        transition: all 0.3s ease;
    }

    #user-input:focus {
        outline: none;
        border-color: #e65100;
        box-shadow: 0 0 5px rgba(241, 104, 58, 0.5);
        background: white;
    }

    #send-button {
        padding: 10px 15px;
        border: none;
        border-radius: 5px;
        background: #f1683a;
        color: white;
        cursor: pointer;
        transition: background 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    #send-button:hover {
        background: #e65100;
    }

    #send-button i {
        font-size: 16px;
    }

    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        margin-bottom: 5px;
    }

    .typing-indicator span {
        width: 6px;
        height: 6px;
        background-color: white;
        border-radius: 50%;
        animation: typingBounce 1.4s infinite;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }

    .booking-form {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }

    .search-box {
        display: flex;
        gap: 5px;
        margin-top: 10px;
    }

    .search-box input {
        flex: 1;
        padding: 8px;
        border: 1px solid #f1683a;
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.9);
    }

    .search-box button {
        padding: 8px 15px;
        background: #f1683a;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .highlight-attraction {
        border-left: 3px solid #f1683a;
        padding-left: 8px;
        margin: 8px 0;
        font-weight: 500;
    }

    #voice-search-button {
        padding: 10px;
        background: #f1683a;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    #voice-search-button.listening {
        background: #e65100;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    .message-feedback {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 5px;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
    }

    .message-feedback button {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        cursor: pointer;
        padding: 2px 5px;
        transition: color 0.3s ease;
    }

    .message-feedback button:hover {
        color: #f1683a;
    }

    #search-section {
        margin-bottom: 10px;
    }
</style>

<script>
    let currentMonument = null;
    let currentState = 'initial';

    function toggleChat() {
        const body = document.getElementById('chatbot-body');
        const icon = document.getElementById('chat-toggle-icon');
        if (body.style.display === 'none') {
            body.style.display = 'block';
            icon.style.transform = 'rotate(180deg)';
            if (document.getElementById('chatbox').children.length === 0) {
                addBotMessage("Welcome to the Monuments Assistant! Please select a monument from the dropdown menu above to get started.");
            }
        } else {
            body.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
        }
    }

    function showTypingIndicator() {
        const chatbox = document.getElementById("chatbox");
        const indicator = document.createElement("div");
        indicator.className = "typing-indicator";
        indicator.id = "typing-indicator";
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement("span");
            indicator.appendChild(dot);
        }
        
        chatbox.appendChild(indicator);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById("typing-indicator");
        if (indicator) {
            indicator.remove();
        }
    }

    function selectMonumentFromDropdown(monumentId) {
        if (monumentId) {
            currentMonument = monumentId;
            document.getElementById('info-tabs').style.display = 'block';
            showTab('overview');
            sendOption('view_info');
        } else {
            currentMonument = null;
            document.getElementById('info-tabs').style.display = 'none';
            addBotMessage("Please select a monument from the dropdown menu to view its details.");
        }
    }

    function showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });

        const selectedTab = document.getElementById(tabName + '-tab');
        selectedTab.style.display = 'block';
        document.querySelector(`button[onclick="showTab('${tabName}')"]`).classList.add('active');
    }

    function addUserMessage(message) {
        const chatbox = document.getElementById("chatbox");
        const userMessage = document.createElement("div");
        userMessage.className = "message user";
        userMessage.textContent = message;
        chatbox.appendChild(userMessage);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function addBotMessage(message) {
        const chatbox = document.getElementById("chatbox");
        const botMessage = document.createElement("div");
        botMessage.className = "message bot";
        botMessage.textContent = message;
        
        if (message.length > 40) {
            addFeedbackButtons(botMessage);
        }
        
        chatbox.appendChild(botMessage);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function addFeedbackButtons(messageElement) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'message-feedback';
        feedbackDiv.innerHTML = `
            <span>Was this helpful?</span>
            <button onclick="provideMessageFeedback(this, true)"><i class="fas fa-thumbs-up"></i></button>
            <button onclick="provideMessageFeedback(this, false)"><i class="fas fa-thumbs-down"></i></button>
        `;
        messageElement.appendChild(feedbackDiv);
    }

    function provideMessageFeedback(button, isPositive) {
        const feedbackDiv = button.parentElement;
        feedbackDiv.innerHTML = isPositive ? 
            'Thanks for your feedback!' : 
            'Thanks for your feedback. We\'ll work to improve this.';
        
        console.log(`User provided ${isPositive ? 'positive' : 'negative'} feedback`);
    }

    function sendOption(option) {
        addUserMessage("You selected: " + option.replace('_', ' '));
        showTypingIndicator();
        
        fetch('/chatbot/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ option: option, currentMonument: currentMonument, currentState: currentState })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            addBotMessage(data.response);
            if (data.monument) {
                currentMonument = data.monument;
            }
            if (data.state) {
                currentState = data.state;
            }
            if (data.html) {
                const chatbox = document.getElementById("chatbox");
                const botMessage = document.createElement("div");
                botMessage.className = "message bot";
                botMessage.innerHTML = data.html;
                chatbox.appendChild(botMessage);
                chatbox.scrollTop = chatbox.scrollHeight;
            }
            if (data.tabs) {
                updateTabs(data.tabs);
            }
        })
        .catch(error => {
            hideTypingIndicator();
            addBotMessage("Sorry, I encountered an error. Please try again.");
            console.error("Error:", error);
        });
    }

    function selectMonument(monumentId) {
        currentMonument = monumentId;
        document.getElementById('monument-dropdown').value = monumentId;
        document.getElementById('info-tabs').style.display = 'block';
        showTab('overview');
        sendOption('view_info');
    }

    function updateTabs(tabs) {
        document.getElementById('overview-tab').innerHTML = tabs.overview;
        document.getElementById('transport-tab').innerHTML = tabs.transport;
        document.getElementById('food-tab').innerHTML = tabs.food;
        document.getElementById('shopping-tab').innerHTML = tabs.shopping;
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            sendUserMessage();
        }
    }

    function performSearch() {
        const searchQuery = document.getElementById('search-input').value.trim();
        if (searchQuery.length > 2) {
            addUserMessage(`Searching for: ${searchQuery}`);
            searchMonuments(searchQuery);
        } else {
            addBotMessage("Please enter a more specific search term.");
        }
    }

    function searchMonuments(query) {
        query = query.toLowerCase();
        const results = Object.entries(MONUMENTS).filter(([id, monument]) => {
            return monument.name.toLowerCase().includes(query) || 
                   monument.location.toLowerCase().includes(query) ||
                   monument.description.toLowerCase().includes(query);
        });
        
        if (results.length === 0) {
            addBotMessage("No monuments found matching your search. Try another term or browse the complete list:");
            sendOption('list_monuments');
            return;
        }
        
        let searchResults = '<ul class="monument-list">';
        results.forEach(([id, monument]) => {
            searchResults += `<li onclick="selectMonument('${id}')">${monument.name} - ${monument.location}</li>`;
        });
        searchResults += '</ul>';
        
        addBotMessage(`Found ${results.length} monuments matching your search:`);
        
        const chatbox = document.getElementById("chatbox");
        const resultMessage = document.createElement("div");
        resultMessage.className = "message bot";
        resultMessage.innerHTML = searchResults;
        chatbox.appendChild(resultMessage);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function getNearbyAttractions() {
        if (!currentMonument || !(currentMonument in MONUMENTS)) {
            addBotMessage("Please select a monument first to view nearby attractions.");
            return;
        }
        
        const monument = MONUMENTS[currentMonument];
        if (!monument.nearby_monuments || monument.nearby_monuments.length === 0) {
            addBotMessage(`Sorry, I don't have information about nearby attractions for ${monument.name}.`);
            return;
        }
        
        let attractionsList = `<div class="info-section"><h4>Nearby Attractions to ${monument.name}</h4><ul>`;
        monument.nearby_monuments.forEach(attraction => {
            attractionsList += `<li>${attraction}</li>`;
        });
        attractionsList += '</ul></div>';
        
        addBotMessage(`Here are attractions near ${monument.name}:`);
        
        const chatbox = document.getElementById("chatbox");
        const botMessage = document.createElement("div");
        botMessage.className = "message bot";
        botMessage.innerHTML = attractionsList;
        chatbox.appendChild(botMessage);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function sendUserMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (message) {
            addUserMessage(message);
            input.value = '';
            showTypingIndicator();
            
            setTimeout(() => {
                hideTypingIndicator();
                
                if (message.toLowerCase().includes('book') && (message.toLowerCase().includes('ticket') || message.toLowerCase().includes('tickets'))) {
                    sendOption('book_ticket');
                } else if (message.toLowerCase().includes('cancel') && (message.toLowerCase().includes('ticket') || message.toLowerCase().includes('booking'))) {
                    sendOption('cancel_ticket');
                } else if (message.toLowerCase().includes('list') || (message.toLowerCase().includes('show') && message.toLowerCase().includes('monuments'))) {
                    sendOption('list_monuments');
                } else if (message.toLowerCase().includes('help') || message.toLowerCase().includes('guide') || message.toLowerCase().includes('assistance')) {
                    sendOption('help');
                } else if (message.toLowerCase().includes('info') || message.toLowerCase().includes('details') || message.toLowerCase().includes('about')) {
                    sendOption('view_info');
                } else if (message.toLowerCase().includes('nearby') || (message.toLowerCase().includes('close') && message.toLowerCase().includes('attractions'))) {
                    if (currentMonument) {
                        getNearbyAttractions();
                    } else {
                        addBotMessage("Please select a monument first to view nearby attractions.");
                    }
                } else if (message.toLowerCase().includes('search') || message.toLowerCase().includes('find')) {
                    const searchTerms = message.replace(/search|find|for/gi, '').trim();
                    if (searchTerms.length > 2) {
                        searchMonuments(searchTerms);
                    } else {
                        addBotMessage("Please specify what you're looking for. For example: 'search for Delhi monuments' or 'find temples'");
                    }
                } else {
                    const allMonuments = Object.entries(MONUMENTS);
                    
                    const monumentFound = allMonuments.find(([_, monument]) => 
                        message.toLowerCase().includes(monument.name.toLowerCase())
                    );
                    
                    const partialMatch = !monumentFound ? allMonuments.find(([_, monument]) => 
                        monument.name.toLowerCase().split(' ').some(word => message.toLowerCase().includes(word.toLowerCase()) && word.length > 3) ||
                        monument.location.toLowerCase().split(' ').some(word => message.toLowerCase().includes(word.toLowerCase()) && word.length > 3)
                    ) : null;
                    
                    if (monumentFound) {
                        selectMonument(monumentFound[0]);
                    } else if (partialMatch) {
                        addBotMessage(`I think you're asking about ${partialMatch[1].name}. Let me show you details:`);
                        selectMonument(partialMatch[0]);
                    } else {
                        if (message.length > 3) {
                            searchMonuments(message);
                        } else {
                            addBotMessage("I'm not sure what you're looking for. You can try:\n1. Selecting a monument from the dropdown\n2. Asking about booking tickets\n3. Getting a list of monuments\n4. Using search with a specific term");
                        }
                    }
                }
            }, 500);
        }
    }

    function populateDropdownByLocation() {
        const dropdown = document.getElementById('monument-dropdown');
        
        const locations = [...new Set(Object.values(MONUMENTS).map(m => m.location.split(',')[0].trim()))];
        
        while (dropdown.options.length > 1) {
            dropdown.remove(1);
        }
        
        locations.forEach(location => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = location;
            
            Object.entries(MONUMENTS).forEach(([id, monument]) => {
                if (monument.location.startsWith(location)) {
                    const option = document.createElement('option');
                    option.value = id;
                    option.text = monument.name;
                    optgroup.appendChild(option);
                }
            });
            
            dropdown.appendChild(optgroup);
        });
    }

    function addVoiceSearch() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const voiceButton = document.createElement('button');
            voiceButton.id = 'voice-search-button';
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceButton.title = 'Search by voice';
            voiceButton.onclick = startVoiceRecognition;
            
            document.getElementById('prompt-box').insertBefore(
                voiceButton,
                document.getElementById('send-button')
            );
        }
    }

    function startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        const voiceButton = document.getElementById('voice-search-button');
        voiceButton.classList.add('listening');
        addBotMessage("Listening...");
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('user-input').value = transcript;
            voiceButton.classList.remove('listening');
            sendUserMessage();
        };
        
        recognition.onerror = function(event) {
            voiceButton.classList.remove('listening');
            addBotMessage("Sorry, I couldn't hear that. Please try again.");
        };
        
        recognition.onend = function() {
            voiceButton.classList.remove('listening');
        };
        
        recognition.start();
    }

    function initChatbot() {
        populateDropdownByLocation();
        addVoiceSearch();
        
        setTimeout(() => {
            if (document.getElementById('chatbot-body').style.display === 'none') {
                toggleChat();
            }
        }, 2000);
    }

    document.addEventListener('DOMContentLoaded', initChatbot);
    document.getElementById('search-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            performSearch();
        }
    });

    function redirectToBooking(monumentId) {
        const monument = MONUMENTS[monumentId];
        if (monument) {
            window.location.href = `/booking?monument=${encodeURIComponent(monument.name)}`;
        } else {
            window.location.href = '/booking';
        }
    }
</script>
'''

# Route for getting the chatbot widget HTML
@chatbot_bp.route('/widget')
def get_widget():
    return render_template_string(chatbot_widget)

# Helper function to determine best transport option
def get_best_transport_option(monument):
    if "airport" in monument["transportation"]["nearest_airport"].lower() and "km" in monument["transportation"]["nearest_airport"].lower():
        airport_distance = int(''.join(filter(str.isdigit, monument["transportation"]["nearest_airport"])))
        if airport_distance <= 15:
            return "taxi from the airport"
        else:
            return "train or bus, followed by local transport"
    else:
        return "local transport such as auto-rickshaws or taxis"

# Route for processing the selected option and returning a response
@chatbot_bp.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        option = data.get('option', '')
        current_monument = data.get('currentMonument')
        current_state = data.get('currentState', 'initial')

        if not option:
            return jsonify({
                'response': "Sorry, I couldn't understand that request.",
                'state': current_state
            })

        if option == 'list_monuments':
            monuments_list = '<ul class="monument-list">'
            for monument_id, monument in MONUMENTS.items():
                monuments_list += f'<li onclick="selectMonument(\'{monument_id}\')">{monument["name"]} - {monument["location"]}</li>'
            monuments_list += '</ul>'
            return jsonify({
                'response': "Here are the available monuments. Click on any monument to view its details:",
                'html': monuments_list,
                'state': 'browsing'
            })

        elif option == 'view_info':
            if current_monument and current_monument in MONUMENTS:
                monument = MONUMENTS[current_monument]
                
                tabs = {
                    'overview': f'''
                        <div class="info-section">
                            <h4>{monument["name"]}</h4>
                            <p><strong>Location:</strong> {monument["location"]}</p>
                            <p><strong>Description:</strong> {monument["description"]}</p>
                            <p><strong>Timings:</strong> {monument["timings"]}</p>
                            <p><strong>Entry Fee:</strong></p>
                            <ul>
                                <li>Indian: {monument["entry_fee"]["indian"]}</li>
                                <li>Foreigner: {monument["entry_fee"]["foreigner"]}</li>
                                <li>Children under 15: {monument["entry_fee"]["children_under_15"]}</li>
                            </ul>
                            <p><strong>Best Time to Visit:</strong> {monument["best_time_to_visit"]}</p>
                            <p><strong>Nearby Attractions:</strong></p>
                            <ul>
                                {"".join([f"<li>{attraction}</li>" for attraction in monument.get("nearby_monuments", [])])}
                            </ul>
                        </div>
                    ''',
                    'transport': f'''
                        <div class="info-section">
                            <h4>Transportation</h4>
                            <ul>
                                <li><strong>Nearest Airport:</strong> {monument["transportation"]["nearest_airport"]}</li>
                                <li><strong>Nearest Railway:</strong> {monument["transportation"]["nearest_railway"]}</li>
                                <li><strong>Local Transport:</strong> {monument["transportation"]["local_transport"]}</li>
                            </ul>
                            <p><strong>Getting There:</strong> The easiest way to reach {monument["name"]} is by {get_best_transport_option(monument)}.</p>
                        </div>
                    ''',
                    'food': f'''
                        <div class="info-section">
                            <h4>Food Options</h4>
                            <ul>
                                {"".join([f"<li>{food}</li>" for food in monument["food_options"]])}
                            </ul>
                            <h4>Nearby Hotels</h4>
                            <ul>
                                {"".join([f"<li>{hotel}</li>" for hotel in monument["nearby_hotels"]])}
                            </ul>
                        </div>
                    ''',
                    'shopping': f'''
                        <div class="info-section">
                            <h4>Shopping Places</h4>
                            <ul>
                                {"".join([f"<li>{shop}</li>" for shop in monument["shopping_places"]])}
                            </ul>
                            <p><strong>Best Buys:</strong> When visiting {monument["name"]}, look for local handicrafts and souvenirs specific to {monument["location"].split(',')[0]}.</p>
                        </div>
                    '''
                }
                
                return jsonify({
                    'response': f"Here are the details for {monument['name']}:",
                    'tabs': tabs,
                    'monument': current_monument,
                    'state': 'viewing_info'
                })
            else:
                return jsonify({
                    'response': "Please select a monument first:",
                    'html': '<ul class="monument-list">' + ''.join([f'<li onclick="selectMonument(\'{monument_id}\')">{monument["name"]} - {monument["location"]}</li>' for monument_id, monument in MONUMENTS.items()]) + '</ul>',
                    'state': 'browsing'
                })

        elif option == 'book_ticket':
            if current_monument and current_monument in MONUMENTS:
                monument = MONUMENTS[current_monument]
                return jsonify({
                    'response': f"To book tickets for {monument['name']}, please provide the following details:\n• Date of visit\n• Number of adults\n• Number of children\n• Nationality (for ticket pricing)",
                    'html': f'''
                        <div class="booking-form">
                            <p>Ticket prices for {monument['name']}:</p>
                            <ul>
                                <li>Indian: {monument["entry_fee"]["indian"]}</li>
                                <li>Foreigner: {monument["entry_fee"]["foreigner"]}</li>
                                <li>Children under 15: {monument["entry_fee"]["children_under_15"]}</li>
                            </ul>
                            <p>Note: This is a demo. No actual booking will be processed.</p>
                            <button onclick="redirectToBooking('{current_monument}')" class="book-button">Proceed to Booking</button>
                        </div>
                    ''',
                    'monument': current_monument,
                    'state': 'booking'
                })
            else:
                return jsonify({
                    'response': "Please select a monument first before booking tickets:",
                    'html': '<ul class="monument-list">' + ''.join([f'<li onclick="selectMonument(\'{monument_id}\')">{monument["name"]}</li>' for monument_id, monument in MONUMENTS.items()]) + '</ul>',
                    'state': 'browsing'
                })

        elif option == 'cancel_ticket':
            return jsonify({
                'response': "To cancel your ticket, please provide your booking ID and we'll help you with the cancellation process.",
                'html': '<p>Note: This is a demo. No actual cancellation will be processed.</p>',
                'state': 'cancelling'
            })

        elif option == 'contact_info':
            return jsonify({
                'response': "Here's how you can reach us:",
                'html': '''
                    <div class="info-section">
                        <h4>Contact Information</h4>
                        <ul>
                            <li><strong>Email:</strong> support@itihaas.com</li>
                            <li><strong>Phone:</strong> +91 1234567890</li>
                            <li><strong>Address:</strong> 123 Heritage Street, New Delhi, India - 110001</li>
                            <li><strong>Working Hours:</strong> Monday - Saturday, 9:00 AM - 6:00 PM</li>
                        </ul>
                        <h4>Emergency Support</h4>
                        <ul>
                            <li><strong>24/7 Helpline:</strong> +91 9876543210</li>
                            <li><strong>WhatsApp Support:</strong> +91 9876543210</li>
                        </ul>
                        <p><strong>Note:</strong> For immediate assistance, please use our 24/7 helpline or WhatsApp support.</p>
                    </div>
                ''',
                'state': 'contact_info'
            })

        elif option == 'help':
            return jsonify({
                'response': "I can help you with:",
                'html': '''
                    <ul>
                        <li><strong>View Information:</strong> Get details about monuments, including timing, entry fees, and facilities</li>
                        <li><strong>Book Tickets:</strong> Book tickets for your selected monument</li>
                        <li><strong>Cancel Tickets:</strong> Cancel previously booked tickets</li>
                        <li><strong>List Monuments:</strong> See a list of all available monuments</li>
                        <li><strong>Find Nearby Places:</strong> Discover hotels, restaurants, and shopping spots near a monument</li>
                    </ul>
                    <p>Simply select an option or type your question!</p>
                ''',
                'state': 'help'
            })

        else:
            return jsonify({
                'response': "Sorry, I didn't understand that option. Please try again.",
                'state': 'initial'
            })
    
    except Exception as e:
        return jsonify({
            'response': "Sorry, I encountered an unexpected error. Please try again.",
            'state': 'error'
        })

@chatbot_bp.route('/get_monuments')
def get_monuments():
    monuments = []
    for monument_id, monument in MONUMENTS.items():
        monuments.append({
            'id': monument_id,
            'name': monument['name'],
            'location': monument['location']
        })
    return jsonify({'monuments': monuments}) 
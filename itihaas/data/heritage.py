"""Static reference data: heritage sites, heritage hotels and festival calendar.

Kept out of the route functions so it can be reused (map, API, tests) and
eventually moved into the database.
"""

FESTIVAL_SITES = {
    'january': {
        'festivals': ['Makar Sankranti', 'Pongal', 'Lohri', 'Bihu'],
        'sites': ['Great Living Chola Temples', 'Rani-ki-Vav']
    },
    'march': {
        'festivals': ['Holi', 'Maha Shivratri'],
        'sites': ['Khajuraho Group of Monuments', 'Ellora Caves', 'Mahabodhi Temple']
    },
    'august': {
        'festivals': ['Raksha Bandhan', 'Janmashtami', 'Ganesh Chaturthi'],
        'sites': ['Sun Temple Konark', 'Elephanta Caves', 'Jaipur City']
    },
    'october': {
        'festivals': ['Diwali', 'Chhath Puja'],
        'sites': ['Taj Mahal', 'Agra Fort', 'Fatehpur Sikri']
    },
    'december': {
        'festivals': ['Christmas', 'New Year'],
        'sites': ['Churches of Goa', 'Victorian Gothic Mumbai']
    }
}

HERITAGE_SITES = [
    # Agra (Uttar Pradesh)
    {
        "name": "Taj Mahal",
        "description": "An ivory-white marble mausoleum, one of the world's most iconic monuments.",
        "lat": 27.1751,
        "lng": 78.0421
    },
    {
        "name": "Agra Fort",
        "description": "UNESCO World Heritage site, a historical fortress and palace complex.",
        "lat": 27.1797,
        "lng": 78.0216
    },
    {
        "name": "Fatehpur Sikri",
        "description": "Former capital of the Mughal Empire, known for its Persian and Mughal architecture.",
        "lat": 27.0940,
        "lng": 77.6711
    },
    {
        "name": "Itimad-ud-Daulah's Tomb",
        "description": "Known as the 'Baby Taj', this tomb is often regarded as a draft of the Taj Mahal.",
        "lat": 27.1927,
        "lng": 78.0307
    },
    {
        "name": "Akbar's Tomb",
        "description": "The tomb of the great Mughal emperor Akbar, located in Sikandra.",
        "lat": 27.2219,
        "lng": 77.9401
    },
    # Maharashtra
    {
        "name": "Chhatrapati Shivaji Terminus",
        "description": "Historic railway station and UNESCO World Heritage site in Mumbai.",
        "lat": 18.9398,
        "lng": 72.8355
    },
    {
        "name": "Gateway of India",
        "description": "Iconic arch monument built in the early 20th century in Mumbai.",
        "lat": 18.9220,
        "lng": 72.8347
    },
    {
        "name": "Ajanta Caves",
        "description": "Ancient Buddhist cave monuments dating from 2nd century BCE.",
        "lat": 20.5519,
        "lng": 75.7033
    },
    {
        "name": "Ellora Caves",
        "description": "Archaeological site with Hindu, Buddhist and Jain cave temples.",
        "lat": 20.0258,
        "lng": 75.1780
    },
    {
        "name": "Bibi-ka-Maqbara",
        "description": "Known as the 'Taj of the Deccan', architectural marvel in Aurangabad.",
        "lat": 19.9018,
        "lng": 75.3186
    },
    {
        "name": "Sindhudurg Fort",
        "description": "16th-century coastal fort built by Chhatrapati Shivaji Maharaj.",
        "lat": 16.0467,
        "lng": 73.4592
    },
    {
        "name": "Shaniwar Wada",
        "description": "Historical fortification in Pune, former seat of the Peshwa rulers.",
        "lat": 18.5195,
        "lng": 73.8553
    },
    {
        "name": "Pratapgad Fort",
        "description": "Mountain fort significant in Maratha history.",
        "lat": 17.9373,
        "lng": 73.5408
    },
    # Delhi
    {
        "name": "Lotus Temple",
        "description": "Remarkable architecture of the Baháʼí House of Worship.",
        "lat": 28.5535,
        "lng": 77.2588
    },
    {
        "name": "Red Fort",
        "description": "Historic fort complex built in the 17th century.",
        "lat": 28.6562,
        "lng": 77.2410
    },
    {
        "name": "India Gate",
        "description": "War memorial dedicated to soldiers of British Indian Army.",
        "lat": 28.6129,
        "lng": 77.2295
    },
    {
        "name": "Qutub Minar",
        "description": "UNESCO World Heritage site, tallest brick minaret in the world.",
        "lat": 28.5244,
        "lng": 77.1855
    },
    {
        "name": "Humayun's Tomb",
        "description": "1570 Mughal architecture that inspired the Taj Mahal.",
        "lat": 28.5933,
        "lng": 77.2507
    },
    {
        "name": "Jama Masjid",
        "description": "India's largest mosque, built by Mughal Emperor Shah Jahan.",
        "lat": 28.6507,
        "lng": 77.2334
    },
    # Goa
    {
        "name": "Basilica of Bom Jesus",
        "description": "UNESCO World Heritage site containing the remains of St. Francis Xavier.",
        "lat": 15.5009,
        "lng": 73.9116
    },
    {
        "name": "Chapora Fort",
        "description": "Ancient fort offering panoramic views of the Arabian Sea.",
        "lat": 15.6016,
        "lng": 73.7346
    },
    {
        "name": "Fort Aguada",
        "description": "17th-century Portuguese fort and lighthouse.",
        "lat": 15.4989,
        "lng": 73.7633
    },
    {
        "name": "Se Cathedral",
        "description": "Largest church in Asia, dedicated to St. Catherine.",
        "lat": 15.5034,
        "lng": 73.9147
    },
    # Kerala
    {
        "name": "Bekal Fort",
        "description": "Largest fort in Kerala, overlooking the Arabian Sea.",
        "lat": 12.3917,
        "lng": 75.0327
    },
    {
        "name": "Jewish Synagogue",
        "description": "Oldest active synagogue in the Commonwealth of Nations.",
        "lat": 9.9578,
        "lng": 76.2595
    },
    {
        "name": "Krishnapuram Palace",
        "description": "Rare example of Kerala's architectural style.",
        "lat": 9.1672,
        "lng": 76.4994
    },
    {
        "name": "Dutch Palace",
        "description": "Also known as Mattancherry Palace, featuring Kerala murals.",
        "lat": 9.9589,
        "lng": 76.2593
    },
    # Rajasthan
    {
        "name": "Hawa Mahal",
        "description": "Palace with unique honeycomb-like structure in Jaipur.",
        "lat": 26.9239,
        "lng": 75.8267
    },
    {
        "name": "City Palace Jaipur",
        "description": "Complex of courtyards, gardens and buildings in Jaipur.",
        "lat": 26.9258,
        "lng": 75.8237
    },
    {
        "name": "Chittorgarh Fort",
        "description": "Largest fort in India, UNESCO World Heritage site.",
        "lat": 24.8879,
        "lng": 74.6446
    },
    {
        "name": "Jantar Mantar",
        "description": "UNESCO World Heritage site, astronomical observation site.",
        "lat": 26.9247,
        "lng": 75.8243
    },
    # Punjab
    {
        "name": "Golden Temple",
        "description": "Holiest Gurdwara of Sikhism located in Amritsar.",
        "lat": 31.6200,
        "lng": 74.8765
    },
    {
        "name": "Jallianwala Bagh",
        "description": "Historic garden and memorial of national importance.",
        "lat": 31.6205,
        "lng": 74.8797
    },
    {
        "name": "Wagah Border",
        "description": "Famous border crossing between India and Pakistan.",
        "lat": 31.6047,
        "lng": 74.5747
    },
    # Arunachal Pradesh
    {
        "name": "Tawang Monastery",
        "description": "Largest monastery in India and second largest in the world.",
        "lat": 27.5859,
        "lng": 91.8757
    },
    {
        "name": "Ita Fort",
        "description": "Ancient fort with oval-shaped brick structure.",
        "lat": 27.0844,
        "lng": 93.6053
    },
    {
        "name": "Golden Pagoda",
        "description": "Buddhist temple known for its Burmese architecture.",
        "lat": 27.4833,
        "lng": 95.9833
    },
    # Madhya Pradesh
    {
        "name": "Khajuraho Temples",
        "description": "UNESCO World Heritage site known for its nagara-style architecture.",
        "lat": 24.8318,
        "lng": 79.9199
    },
    {
        "name": "Gwalior Fort",
        "description": "Historic fortress and architectural marvel.",
        "lat": 26.2322,
        "lng": 78.1691
    },
    {
        "name": "Orchha Fort",
        "description": "Historical site with multiple temples and palaces.",
        "lat": 25.3505,
        "lng": 78.6409
    },
    # Uttarakhand
    {
        "name": "Badrinath Temple",
        "description": "One of the holiest Hindu temples dedicated to Vishnu.",
        "lat": 30.7433,
        "lng": 79.4938
    },
    {
        "name": "Katarmal Sun Temple",
        "description": "Ancient sun temple from the 9th century.",
        "lat": 29.6366,
        "lng": 79.6266
    },
    # Himachal Pradesh
    {
        "name": "Kangra Fort",
        "description": "Oldest dated fort in India with rich history.",
        "lat": 32.0999,
        "lng": 76.2691
    },
    {
        "name": "Tabo Monastery",
        "description": "Ancient monastery known as the 'Ajanta of the Himalayas'.",
        "lat": 32.0935,
        "lng": 78.3872
    },
    # West Bengal
    {
        "name": "Victoria Memorial",
        "description": "Magnificent marble building dedicated to Queen Victoria.",
        "lat": 22.5448,
        "lng": 88.3426
    },
    {
        "name": "Hazarduari Palace",
        "description": "Palace with 1000 doors in Murshidabad.",
        "lat": 24.1765,
        "lng": 88.2801
    },
    {
        "name": "Bishnupur Terracotta Temples",
        "description": "Group of temples known for terracotta architecture.",
        "lat": 23.0795,
        "lng": 87.3198
    },
    # Jammu and Kashmir
    {
        "name": "Hari Parbat Fort",
        "description": "Historic fort overlooking Srinagar.",
        "lat": 34.1069,
        "lng": 74.8152
    },
    {
        "name": "Pari Mahal",
        "description": "Seven-terraced garden near Srinagar.",
        "lat": 34.0998,
        "lng": 74.8808
    },
    # Odisha
    {
        "name": "Konark Sun Temple",
        "description": "13th-century sun temple, UNESCO World Heritage site.",
        "lat": 19.8876,
        "lng": 86.0945
    },
    {
        "name": "Lingaraja Temple",
        "description": "Ancient temple dedicated to Lord Shiva.",
        "lat": 20.2359,
        "lng": 85.8320
    },
    # Gujarat
    {
        "name": "Rani ki Vav",
        "description": "Intricately designed stepwell, UNESCO World Heritage site.",
        "lat": 23.8593,
        "lng": 72.1023
    },
    {
        "name": "Dwarkadhish Temple",
        "description": "Ancient temple dedicated to Lord Krishna.",
        "lat": 22.2376,
        "lng": 68.9674
    },
    # Telangana
    {
        "name": "Charminar",
        "description": "Iconic monument and mosque in Hyderabad.",
        "lat": 17.3616,
        "lng": 78.4747
    },
    {
        "name": "Golconda Fort",
        "description": "Medieval fort and former diamond trading center.",
        "lat": 17.3833,
        "lng": 78.4011
    },
    {
        "name": "Warangal Fort",
        "description": "13th-century fort with impressive architecture.",
        "lat": 18.0006,
        "lng": 79.5881
    }
]

HERITAGE_HOTELS = [
    # Agra Hotels
    {
        "name": "The Oberoi Amarvilas",
        "description": "5-star luxury hotel with Taj Mahal views, 600m from Taj Mahal",
        "lat": 27.1731,
        "lng": 78.0484,
        "category": "Luxury"
    },
    {
        "name": "ITC Mughal",
        "description": "5-star hotel with Mughal architecture, near Taj Mahal",
        "lat": 27.1662,
        "lng": 78.0298,
        "category": "Luxury"
    },
    # Delhi Hotels
    {
        "name": "The Imperial",
        "description": "Historic 5-star hotel in central Delhi",
        "lat": 28.6264,
        "lng": 77.2189,
        "category": "Luxury"
    },
    {
        "name": "The Taj Mahal Hotel",
        "description": "Luxury hotel near India Gate",
        "lat": 28.6030,
        "lng": 77.2289,
        "category": "Luxury"
    },
    # Jaipur Hotels
    {
        "name": "Rambagh Palace",
        "description": "Former royal residence turned luxury hotel",
        "lat": 26.8980,
        "lng": 75.8183,
        "category": "Heritage"
    },
    {
        "name": "Taj Jai Mahal Palace",
        "description": "Heritage hotel with 18 acres of gardens",
        "lat": 26.9126,
        "lng": 75.8124,
        "category": "Heritage"
    },
    # Mumbai Hotels
    {
        "name": "The Taj Mahal Palace",
        "description": "Iconic 5-star hotel near Gateway of India",
        "lat": 18.9217,
        "lng": 72.8332,
        "category": "Luxury"
    },
    {
        "name": "The Oberoi Mumbai",
        "description": "Luxury hotel with sea views",
        "lat": 18.9257,
        "lng": 72.8212,
        "category": "Luxury"
    },
    # Udaipur Hotels
    {
        "name": "Taj Lake Palace",
        "description": "Luxury hotel in middle of Lake Pichola",
        "lat": 24.5753,
        "lng": 73.6808,
        "category": "Heritage"
    },
    # Varanasi Hotels
    {
        "name": "Taj Ganges",
        "description": "5-star hotel with modern amenities",
        "lat": 25.3176,
        "lng": 83.0065,
        "category": "Luxury"
    },
    # Goa Hotels
    {
        "name": "Taj Fort Aguada Resort",
        "description": "Luxury resort near Fort Aguada",
        "lat": 15.4977,
        "lng": 73.7637,
        "category": "Resort"
    },
    {
        "name": "Park Hyatt Goa Resort",
        "description": "Beachfront luxury resort",
        "lat": 15.2993,
        "lng": 73.9137,
        "category": "Resort"
    },
    # Kerala Hotels
    {
        "name": "Kumarakom Lake Resort",
        "description": "Luxury backwater resort",
        "lat": 9.5977,
        "lng": 76.4216,
        "category": "Resort"
    },
    {
        "name": "The Leela Kovalam",
        "description": "Cliff-top beach resort",
        "lat": 8.3809,
        "lng": 76.9781,
        "category": "Resort"
    },
    # Amritsar Hotels
    {
        "name": "Taj Swarna",
        "description": "Luxury hotel near Golden Temple",
        "lat": 31.6336,
        "lng": 74.8723,
        "category": "Luxury"
    },
    # Hyderabad Hotels
    {
        "name": "Taj Falaknuma Palace",
        "description": "Former Nizam's palace turned luxury hotel",
        "lat": 17.3328,
        "lng": 78.4677,
        "category": "Heritage"
    },
    {
        "name": "ITC Kohenur",
        "description": "Modern luxury hotel in HITEC City",
        "lat": 17.4275,
        "lng": 78.3461,
        "category": "Luxury"
    }
]

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
    "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
    "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
]

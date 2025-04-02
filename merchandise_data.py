from . import db
from .merchandise_models import Merchandise
from .models import Guide, User

def add_clothing_items():
    # First, get or create a default guide
    default_user = User.query.filter_by(email='itihaasdairy@gmail.com').first()
    if not default_user:
        default_user = User(
            email='itihaasdairy@gmail.com',
            password='admin123'
        )
        db.session.add(default_user)
        db.session.flush()  # Get the user ID

    default_guide = Guide.query.filter_by(user_id=default_user.id).first()
    if not default_guide:
        default_guide = Guide(
            user_id=default_user.id,
            name='Admin Guide',
            phone='1234567890',
            experience=5,
            languages=['English', 'Hindi']
        )
        db.session.add(default_guide)
        db.session.flush()  # Get the guide ID

    clothing_items = [
        {
            'name': 'Classic Kurta',
            'description': 'Traditional Indian kurta made from premium cotton fabric. Perfect for both casual and formal occasions.',
            'price': 1299.00,
            'stock': 50,
            'category': 'clothing',
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'guide_id': default_guide.id
        },
        {
            'name': 'Silk Saree',
            'description': 'Elegant silk saree with intricate zari work. A perfect blend of traditional and contemporary design.',
            'price': 3999.00,
            'stock': 30,
            'category': 'clothing',
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'guide_id': default_guide.id
        },
        {
            'name': 'Cotton Salwar Kameez',
            'description': 'Comfortable and stylish salwar kameez set made from pure cotton. Ideal for daily wear.',
            'price': 1499.00,
            'stock': 40,
            'category': 'clothing',
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'guide_id': default_guide.id
        },
        {
            'name': 'Designer Sherwani',
            'description': 'Luxurious sherwani with detailed embroidery work. Perfect for weddings and special occasions.',
            'price': 5999.00,
            'stock': 25,
            'category': 'clothing',
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'guide_id': default_guide.id
        },
        {
            'name': 'Casual Palazzo Set',
            'description': 'Modern palazzo set with matching dupatta. Comfortable and fashionable for any occasion.',
            'price': 999.00,
            'stock': 60,
            'category': 'clothing',
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'guide_id': default_guide.id
        }
    ]

    for item in clothing_items:
        merchandise = Merchandise(**item)
        db.session.add(merchandise)
    
    db.session.commit()
    print("Clothing items added successfully!") 
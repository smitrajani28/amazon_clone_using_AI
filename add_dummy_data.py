#!/usr/bin/env python
import os
import django
import random
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_clone.settings')
django.setup()

from products.models import Category, Product, DailyOffer

# Sample product data
CATEGORIES = [
    {'name': 'Electronics', 'slug': 'electronics'},
    {'name': 'Books', 'slug': 'books'},
    {'name': 'Home & Kitchen', 'slug': 'home-kitchen'},
    {'name': 'Clothing', 'slug': 'clothing'},
    {'name': 'Toys & Games', 'slug': 'toys-games'},
]

PRODUCTS = [
    # Electronics
    {
        'category': 'electronics',
        'name': 'Wireless Bluetooth Headphones',
        'slug': 'wireless-bluetooth-headphones',
        'description': 'High-quality wireless headphones with noise cancellation and 20-hour battery life.',
        'price': Decimal('79.99'),
    },
    {
        'category': 'electronics',
        'name': 'Smart Watch Series 5',
        'slug': 'smart-watch-series-5',
        'description': 'Track your fitness, receive notifications, and more with this advanced smartwatch.',
        'price': Decimal('199.99'),
    },
    {
        'category': 'electronics',
        'name': '4K Ultra HD Smart TV - 55"',
        'slug': '4k-ultra-hd-smart-tv-55',
        'description': 'Immersive viewing experience with stunning 4K resolution and smart features.',
        'price': Decimal('499.99'),
    },
    {
        'category': 'electronics',
        'name': 'Portable Bluetooth Speaker',
        'slug': 'portable-bluetooth-speaker',
        'description': 'Compact speaker with powerful sound and 12-hour battery life.',
        'price': Decimal('39.99'),
    },
    
    # Books
    {
        'category': 'books',
        'name': 'The Art of Programming',
        'slug': 'the-art-of-programming',
        'description': 'A comprehensive guide to modern programming techniques and best practices.',
        'price': Decimal('29.99'),
    },
    {
        'category': 'books',
        'name': 'Mystery at Midnight',
        'slug': 'mystery-at-midnight',
        'description': 'A thrilling mystery novel that will keep you on the edge of your seat.',
        'price': Decimal('14.99'),
    },
    {
        'category': 'books',
        'name': 'Cooking Basics: 101 Recipes',
        'slug': 'cooking-basics-101-recipes',
        'description': 'Learn to cook delicious meals with these simple recipes for beginners.',
        'price': Decimal('19.99'),
    },
    
    # Home & Kitchen
    {
        'category': 'home-kitchen',
        'name': 'Stainless Steel Cookware Set',
        'slug': 'stainless-steel-cookware-set',
        'description': '10-piece cookware set made of high-quality stainless steel.',
        'price': Decimal('129.99'),
    },
    {
        'category': 'home-kitchen',
        'name': 'Robot Vacuum Cleaner',
        'slug': 'robot-vacuum-cleaner',
        'description': 'Smart vacuum that automatically cleans your floors with precision.',
        'price': Decimal('249.99'),
    },
    {
        'category': 'home-kitchen',
        'name': 'Coffee Maker with Grinder',
        'slug': 'coffee-maker-with-grinder',
        'description': 'Brew fresh coffee with this all-in-one coffee maker and grinder.',
        'price': Decimal('89.99'),
    },
    
    # Clothing
    {
        'category': 'clothing',
        'name': 'Men\'s Classic Fit T-Shirt',
        'slug': 'mens-classic-fit-t-shirt',
        'description': 'Comfortable cotton t-shirt available in multiple colors.',
        'price': Decimal('19.99'),
    },
    {
        'category': 'clothing',
        'name': 'Women\'s Running Shoes',
        'slug': 'womens-running-shoes',
        'description': 'Lightweight and supportive shoes perfect for running or everyday wear.',
        'price': Decimal('59.99'),
    },
    {
        'category': 'clothing',
        'name': 'Winter Jacket with Hood',
        'slug': 'winter-jacket-with-hood',
        'description': 'Warm and water-resistant jacket for cold weather.',
        'price': Decimal('89.99'),
    },
    
    # Toys & Games
    {
        'category': 'toys-games',
        'name': 'Building Blocks Set (500 pieces)',
        'slug': 'building-blocks-set-500-pieces',
        'description': 'Creative building blocks for endless fun and learning.',
        'price': Decimal('34.99'),
    },
    {
        'category': 'toys-games',
        'name': 'Board Game Collection',
        'slug': 'board-game-collection',
        'description': 'Set of 5 classic board games for family game night.',
        'price': Decimal('49.99'),
    },
    {
        'category': 'toys-games',
        'name': 'Remote Control Car',
        'slug': 'remote-control-car',
        'description': 'Fast and durable RC car with a range of 100 meters.',
        'price': Decimal('45.99'),
    },
]

# Sample daily offers
DAILY_OFFERS = [
    {
        'title': 'Flash Sale: 50% Off Electronics',
        'description': 'Limited time offer on selected electronics. Hurry before stock runs out!',
        'product_category': 'electronics',
    },
    {
        'title': 'Buy 2 Get 1 Free on Books',
        'description': 'Special offer on all books. Perfect time to stock up your library!',
        'product_category': 'books',
    },
    {
        'title': 'Home Essentials Sale',
        'description': 'Great deals on kitchen appliances and home goods. Save up to 30%!',
        'product_category': 'home-kitchen',
    },
    {
        'title': 'Summer Fashion Clearance',
        'description': 'End of season sale on all summer clothing. Discounts up to 60%!',
        'product_category': 'clothing',
    },
    {
        'title': 'Holiday Gift Ideas',
        'description': 'Find the perfect gifts for everyone on your list. Special bundles available!',
        'product_category': 'toys-games',
    },
]

def create_dummy_data():
    # Create categories
    categories = {}
    for cat_data in CATEGORIES:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            slug=cat_data['slug']
        )
        categories[cat_data['slug']] = category
        # Define constant for status messages
        STATUS_CREATED = 'Created'
        STATUS_EXISTS = 'Already exists'
        
        action = STATUS_CREATED if created else STATUS_EXISTS
        print(f"{action}: Category '{category.name}'")
    
    # Create products
    products_by_category = {}
    for prod_data in PRODUCTS:
        category = categories[prod_data['category']]
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'slug': prod_data['slug'],
                'category': category,
                'description': prod_data['description'],
                'price': prod_data['price'],
                'available': True
            }
        )
        
        if prod_data['category'] not in products_by_category:
            products_by_category[prod_data['category']] = []
        products_by_category[prod_data['category']].append(product)
        
        action = STATUS_CREATED if created else STATUS_EXISTS
        print(f"{action}: Product '{product.name}' in category '{category.name}'")
    
    # Create daily offers
    for offer_data in DAILY_OFFERS:
        category = offer_data['product_category']
        if category in products_by_category and products_by_category[category]:
            # Link to a random product from the specified category
            product = random.choice(products_by_category[category])
            
            offer, created = DailyOffer.objects.get_or_create(
                title=offer_data['title'],
                defaults={
                    'description': offer_data['description'],
                    'product': product,
                    'active': True,
                    'url': product.get_absolute_url()
                }
            )
            
            action = STATUS_CREATED if created else STATUS_EXISTS
            print(f"{action}: Daily Offer '{offer.title}' linked to '{product.name}'")

if __name__ == '__main__':
    print("Adding dummy data to the database...")
    create_dummy_data()
    print("Done!")
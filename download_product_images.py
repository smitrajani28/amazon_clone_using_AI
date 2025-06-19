#!/usr/bin/env python
import os
import django
import requests
from django.core.files.base import ContentFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_clone.settings')
django.setup()

from products.models import Product, Category

# Dictionary mapping product names to image URLs
PRODUCT_IMAGES = {
    'Wireless Bluetooth Headphones': 'https://images-na.ssl-images-amazon.com/images/I/71BKQhFzDmL._AC_SL1500_.jpg',
    'Smart Watch Series 5': 'https://images-na.ssl-images-amazon.com/images/I/71wu+HMAKBL._AC_SL1500_.jpg',
    '4K Ultra HD Smart TV - 55"': 'https://images-na.ssl-images-amazon.com/images/I/71ihMv1q+kL._AC_SL1500_.jpg',
    'Portable Bluetooth Speaker': 'https://images-na.ssl-images-amazon.com/images/I/71JB6hM6Z6L._AC_SL1500_.jpg',
    'The Art of Programming': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
    'Mystery at Midnight': 'https://images-na.ssl-images-amazon.com/images/I/51jNORv6nQL._SX340_BO1,204,203,200_.jpg',
    'Cooking Basics: 101 Recipes': 'https://images-na.ssl-images-amazon.com/images/I/51tpMCGzUWL._SX398_BO1,204,203,200_.jpg',
    'Stainless Steel Cookware Set': 'https://images-na.ssl-images-amazon.com/images/I/71tTYy7kTOL._AC_SL1500_.jpg',
    'Robot Vacuum Cleaner': 'https://images-na.ssl-images-amazon.com/images/I/71Vhcq7pKmL._AC_SL1500_.jpg',
    'Coffee Maker with Grinder': 'https://images-na.ssl-images-amazon.com/images/I/81luUhz7ZlL._AC_SL1500_.jpg',
    'Men\'s Classic Fit T-Shirt': 'https://images-na.ssl-images-amazon.com/images/I/71UXuqXZGFL._AC_UL1500_.jpg',
    'Women\'s Running Shoes': 'https://images-na.ssl-images-amazon.com/images/I/81ZYZ9yl1hL._AC_UL1500_.jpg',
    'Winter Jacket with Hood': 'https://images-na.ssl-images-amazon.com/images/I/71Hx1KFcFnL._AC_UL1500_.jpg',
    'Building Blocks Set (500 pieces)': 'https://images-na.ssl-images-amazon.com/images/I/81lAPl4nJqL._AC_SL1500_.jpg',
    'Board Game Collection': 'https://images-na.ssl-images-amazon.com/images/I/91dDxgAyGOL._AC_SL1500_.jpg',
    'Remote Control Car': 'https://images-na.ssl-images-amazon.com/images/I/71S-XwHG4HL._AC_SL1500_.jpg',
}

def download_image(url):
    """Download image from URL and return as ContentFile"""
    try:
        response = requests.get(url, verify=True)  # Enable SSL verification
        if response.status_code == 200:
            return ContentFile(response.content)
        else:
            print(f"Failed to download image: {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def add_product_images():
    """Add images to products based on their names"""
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Get all products
    products = Product.objects.all()
    
    for product in products:
        # Get image URL for this product
        image_url = PRODUCT_IMAGES.get(product.name)
        if not image_url:
            print(f"No image URL found for product: {product.name}")
            continue
        
        # Download image
        print(f"Downloading image for product: {product.name}")
        image_content = download_image(image_url)
        
        if image_content:
            # Generate filename from product slug
            filename = f"{product.slug}.jpg"
            
            # Save image to product
            product.image.save(filename, image_content, save=True)
            print(f"Added image to product: {product.name}")
        else:
            print(f"Failed to add image to product: {product.name}")

if __name__ == '__main__':
    print("Adding images to products...")
    add_product_images()
    print("Done!")
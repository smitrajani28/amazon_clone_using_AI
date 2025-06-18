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
    'Wireless Bluetooth Headphones': 'https://m.media-amazon.com/images/I/61CGHv6kmWL._AC_UY327_FMwebp_QL65_.jpg',
    'Smart Watch Series 5': 'https://m.media-amazon.com/images/I/71bhWgQK-cL._AC_UY327_FMwebp_QL65_.jpg',
    '4K Ultra HD Smart TV - 55"': 'https://m.media-amazon.com/images/I/81nC4u9eqYL._AC_UY327_FMwebp_QL65_.jpg',
    'Portable Bluetooth Speaker': 'https://m.media-amazon.com/images/I/71Q-Vp2j+PL._AC_UY327_FMwebp_QL65_.jpg',
    'The Art of Programming': 'https://m.media-amazon.com/images/I/71KL6aEpKrL._AC_UY327_FMwebp_QL65_.jpg',
    'Mystery at Midnight': 'https://m.media-amazon.com/images/I/81bGKUa1e0L._AC_UY327_FMwebp_QL65_.jpg',
    'Cooking Basics: 101 Recipes': 'https://m.media-amazon.com/images/I/81-QB7nDh4L._AC_UY327_FMwebp_QL65_.jpg',
    'Stainless Steel Cookware Set': 'https://m.media-amazon.com/images/I/71VbHaAqbML._AC_UY327_FMwebp_QL65_.jpg',
    'Robot Vacuum Cleaner': 'https://m.media-amazon.com/images/I/81Nw4loNFPL._AC_UY327_FMwebp_QL65_.jpg',
    'Coffee Maker with Grinder': 'https://m.media-amazon.com/images/I/71WtwEvYDOS._AC_UY327_FMwebp_QL65_.jpg',
    'Men\'s Classic Fit T-Shirt': 'https://m.media-amazon.com/images/I/61+fasySBQL._AC_UL640_FMwebp_QL65_.jpg',
    'Women\'s Running Shoes': 'https://m.media-amazon.com/images/I/71MG0EzCU4L._AC_UL640_FMwebp_QL65_.jpg',
    'Winter Jacket with Hood': 'https://m.media-amazon.com/images/I/81nC+7J5thL._AC_UL640_FMwebp_QL65_.jpg',
    'Building Blocks Set (500 pieces)': 'https://m.media-amazon.com/images/I/71qsvtqJWML._AC_UL640_FMwebp_QL65_.jpg',
    'Board Game Collection': 'https://m.media-amazon.com/images/I/81YrGrKHb-L._AC_UL640_FMwebp_QL65_.jpg',
    'Remote Control Car': 'https://m.media-amazon.com/images/I/71Swqqe7XAL._AC_UL640_FMwebp_QL65_.jpg',
}

# Alternative image URLs if the above don't work
FALLBACK_IMAGES = {
    'Electronics': 'https://via.placeholder.com/400x400.png?text=Electronics',
    'Books': 'https://via.placeholder.com/400x400.png?text=Books',
    'Home & Kitchen': 'https://via.placeholder.com/400x400.png?text=Home+and+Kitchen',
    'Clothing': 'https://via.placeholder.com/400x400.png?text=Clothing',
    'Toys & Games': 'https://via.placeholder.com/400x400.png?text=Toys+and+Games',
}

def download_image(url):
    """Download image from URL and return as ContentFile"""
    try:
        response = requests.get(url, verify=False)  # Disable SSL verification
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
            # Try fallback image based on category
            category_name = product.category.name
            image_url = FALLBACK_IMAGES.get(category_name)
            if not image_url:
                print(f"No fallback image found for category: {category_name}")
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
            # Try fallback image based on category
            category_name = product.category.name
            fallback_url = FALLBACK_IMAGES.get(category_name)
            if fallback_url:
                print(f"Trying fallback image for category: {category_name}")
                fallback_content = download_image(fallback_url)
                if fallback_content:
                    filename = f"{product.slug}_fallback.jpg"
                    product.image.save(filename, fallback_content, save=True)
                    print(f"Added fallback image to product: {product.name}")

if __name__ == '__main__':
    print("Adding images to products...")
    add_product_images()
    print("Done!")
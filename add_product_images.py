#!/usr/bin/env python
import os
import django
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_clone.settings')
django.setup()

from products.models import Product, Category

def add_product_images():
    """Add placeholder images to products based on their category"""
    # Create media directory if it doesn't exist
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'products')
    os.makedirs(media_dir, exist_ok=True)
    
    # Get all products
    products = Product.objects.all()
    
    for product in products:
        # Skip if product already has an image
        if product.image:
            print(f"Product '{product.name}' already has an image, skipping.")
            continue
        
        # Create a placeholder image based on category
        category_name = product.category.name.lower().replace(' & ', '_').replace(' ', '_')
        placeholder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       'static', 'images', f'{category_name}_placeholder.jpg')
        
        # If category placeholder doesn't exist, use a generic one
        if not os.path.exists(placeholder_path):
            placeholder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           'static', 'images', 'product_placeholder.jpg')
        
        # Check if the generic placeholder exists
        if not os.path.exists(placeholder_path):
            print(f"No placeholder image found for product: {product.name}")
            continue
        
        # Generate filename from product slug
        filename = f"{product.slug}.jpg"
        
        try:
            # Open the placeholder image
            with open(placeholder_path, 'rb') as f:
                image_content = f.read()
            
            # Save image to product
            product.image.save(filename, ContentFile(image_content), save=True)
            print(f"Added image to product: {product.name}")
        except Exception as e:
            print(f"Error adding image to product {product.name}: {e}")

def create_placeholder_images():
    """Create placeholder images for each category"""
    # Create static/images directory if it doesn't exist
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Create a generic product placeholder
    generic_path = os.path.join(images_dir, 'product_placeholder.jpg')
    if not os.path.exists(generic_path):
        # Create a simple colored rectangle as placeholder
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a blank image with a white background
            img = Image.new('RGB', (400, 400), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            
            # Draw a colored rectangle
            d.rectangle([(50, 50), (350, 350)], fill=(200, 200, 200))
            
            # Add text "Product Image"
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except IOError:
                font = ImageFont.load_default()
                
            d.text((100, 180), "Product Image", fill=(0, 0, 0), font=font)
            
            # Save the image
            img.save(generic_path)
            print(f"Created generic placeholder image at {generic_path}")
        except ImportError:
            print("PIL not installed, skipping placeholder image creation")
            return
    
    # Create category-specific placeholders
    categories = Category.objects.all()
    colors = {
        'electronics': (173, 216, 230),  # Light blue
        'books': (144, 238, 144),        # Light green
        'home_kitchen': (255, 182, 193), # Light pink
        'clothing': (255, 218, 185),     # Peach
        'toys_games': (221, 160, 221),   # Plum
    }
    
    for category in categories:
        category_slug = category.name.lower().replace(' & ', '_').replace(' ', '_')
        category_path = os.path.join(images_dir, f'{category_slug}_placeholder.jpg')
        
        if not os.path.exists(category_path):
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Get color for this category or use a default
                color = colors.get(category_slug, (200, 200, 200))
                
                # Create a blank image with a white background
                img = Image.new('RGB', (400, 400), color=(255, 255, 255))
                d = ImageDraw.Draw(img)
                
                # Draw a colored rectangle
                d.rectangle([(50, 50), (350, 350)], fill=color)
                
                # Add text with category name
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except IOError:
                    font = ImageFont.load_default()
                    
                d.text((100, 180), f"{category.name}", fill=(0, 0, 0), font=font)
                
                # Save the image
                img.save(category_path)
                print(f"Created placeholder image for {category.name} at {category_path}")
            except ImportError:
                print("PIL not installed, skipping placeholder image creation")
                return

if __name__ == '__main__':
    print("Creating placeholder images...")
    create_placeholder_images()
    
    print("Adding images to products...")
    add_product_images()
    
    print("Done!")
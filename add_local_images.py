#!/usr/bin/env python
import os
import django
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_clone.settings')
django.setup()

from products.models import Product, Category

def create_image_for_product(product):
    """Create a custom image for a product"""
    # Create a blank image with a white background
    width, height = 400, 400
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Get color based on category
    colors = {
        'Electronics': (173, 216, 230),  # Light blue
        'Books': (144, 238, 144),        # Light green
        'Home & Kitchen': (255, 182, 193), # Light pink
        'Clothing': (255, 218, 185),     # Peach
        'Toys & Games': (221, 160, 221), # Plum
    }
    category_name = product.category.name
    color = colors.get(category_name, (200, 200, 200))
    
    # Draw a colored rectangle
    d.rectangle([(50, 50), (350, 350)], fill=color)
    
    # Add product name
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Wrap text if it's too long
    product_name = product.name
    max_width = 250
    words = product_name.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        w, h = d.textsize(test_line, font=font) if hasattr(d, 'textsize') else (len(test_line) * 10, 20)
        
        if w <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw text
    y_position = 150
    for line in lines:
        w, h = d.textsize(line, font=font) if hasattr(d, 'textsize') else (len(line) * 10, 20)
        d.text(((width - w) / 2, y_position), line, fill=(0, 0, 0), font=font)
        y_position += h + 10
    
    # Add price
    price_text = f"${product.price}"
    w, h = d.textsize(price_text, font=font) if hasattr(d, 'textsize') else (len(price_text) * 10, 20)
    d.text(((width - w) / 2, 250), price_text, fill=(255, 0, 0), font=font)
    
    # Add category
    category_text = f"Category: {category_name}"
    w, h = d.textsize(category_text, font=font) if hasattr(d, 'textsize') else (len(category_text) * 10, 20)
    d.text(((width - w) / 2, 300), category_text, fill=(0, 0, 0), font=font)
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())

def add_local_images():
    """Add locally generated images to products without images"""
    # Get all products
    products = Product.objects.all()
    
    for product in products:
        # Skip if product already has an image
        if product.image and product.image.name:
            print(f"Product '{product.name}' already has an image, skipping.")
            continue
        
        print(f"Creating image for product: {product.name}")
        image_content = create_image_for_product(product)
        
        # Generate filename from product slug
        filename = f"{product.slug}_local.jpg"
        
        # Save image to product
        product.image.save(filename, image_content, save=True)
        print(f"Added local image to product: {product.name}")

if __name__ == '__main__':
    print("Adding local images to products without images...")
    add_local_images()
    print("Done!")
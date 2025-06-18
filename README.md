# Amazon Clone E-commerce Website

This is an Amazon-like e-commerce website built with Django. The project aims to replicate the core functionality and UI of Amazon.

## Features

- User authentication and profile management
- Product browsing by categories
- Product detail pages
- Shopping cart functionality
- Order processing
- Responsive Amazon-like UI

## Project Structure

- `products`: App for managing products and categories
- `accounts`: App for user authentication and profiles
- `cart`: App for shopping cart functionality
- `orders`: App for order processing
- `templates`: HTML templates with Amazon-like UI
- `static`: CSS, JavaScript, and image files

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`
8. Access the admin panel at `http://127.0.0.1:8000/admin/` to add products and categories

## Technologies Used

- Django
- HTML/CSS
- Bootstrap 5
- JavaScript
- Font Awesome

## Next Steps

- Implement search functionality
- Add product reviews and ratings
- Integrate payment processing
- Add wish lists
- Implement product recommendations
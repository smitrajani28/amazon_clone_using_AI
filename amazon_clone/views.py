from django.shortcuts import render
from products.models import Product, Category, DailyOffer

def home(request):
    products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()
    daily_offers = DailyOffer.objects.filter(active=True)[:5]
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'daily_offers': daily_offers
    })
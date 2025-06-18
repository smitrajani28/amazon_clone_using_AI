from decimal import Decimal
from django.conf import settings
from products.models import Product
from .models import Cart as CartModel, CartItem

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.request = request
        self.cart_model = self._get_cart_model()
        self.cart_items = CartItem.objects.filter(cart=self.cart_model)
    
    def _get_cart_model(self):
        """Get or create a cart model instance."""
        cart_id = self.request.session.get('cart_id')
        if not cart_id:
            cart = CartModel.objects.create()
            self.request.session['cart_id'] = cart.id
        else:
            try:
                cart = CartModel.objects.get(id=cart_id)
            except CartModel.DoesNotExist:
                cart = CartModel.objects.create()
                self.request.session['cart_id'] = cart.id
        
        if self.request.user.is_authenticated and not cart.user:
            cart.user = self.request.user
            cart.save()
        
        return cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        try:
            cart_item = CartItem.objects.get(cart=self.cart_model, product=product)
            if override_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=self.cart_model, product=product, quantity=quantity)
    
    def remove(self, product):
        """Remove a product from the cart."""
        try:
            cart_item = CartItem.objects.get(cart=self.cart_model, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    
    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database."""
        for item in self.cart_items:
            item_dict = {
                'product': item.product,
                'quantity': item.quantity,
                'price': item.product.price,
                'total_price': item.get_cost(),
                'get_cost': item.get_cost(),
            }
            yield item_dict
    
    def __len__(self):
        """Count all items in the cart."""
        return sum(item.quantity for item in self.cart_items)
    
    def get_total_price(self):
        """Calculate the total price of items in the cart."""
        return self.cart_model.get_total_price()
    
    def clear(self):
        """Remove all items from the cart."""
        self.cart_items.delete()
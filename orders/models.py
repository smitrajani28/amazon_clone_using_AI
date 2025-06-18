from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    DELIVERY_CHOICES = (
        ('standard', 'Standard Delivery (3-5 days)'),
        ('express', 'Express Delivery (1-2 days)'),
        ('same_day', 'Same Day Delivery'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField(null=True, blank=True)  # Made nullable temporarily
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='standard')
    delivery_date = models.DateField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order {self.id} - {self.user.username}'
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    def calculate_delivery_date(self):
        today = timezone.now().date()
        if self.delivery_method == 'same_day':
            return today
        elif self.delivery_method == 'express':
            return today + timezone.timedelta(days=2)
        else:  # standard
            return today + timezone.timedelta(days=5)
    
    def save(self, *args, **kwargs):
        if not self.delivery_date:
            self.delivery_date = self.calculate_delivery_date()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
    
    def get_total_price(self):
        return self.price * self.quantity

class DeliveryUpdate(models.Model):
    STATUS_CHOICES = (
        ('order_placed', 'Order Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('delayed', 'Delayed'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_updates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.order.id} - {self.status} - {self.timestamp}'
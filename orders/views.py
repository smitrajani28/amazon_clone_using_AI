from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem, DeliveryUpdate
from .forms import DeliveryMethodForm
from cart.cart import Cart

# Define constant for order detail URL
ORDER_DETAIL_URL = 'orders:order_detail'

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery_updates = order.delivery_updates.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'delivery_updates': delivery_updates
    })

@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        # Get shipping address from form
        shipping_address = request.POST.get('shipping_address', '')
        delivery_method = request.POST.get('delivery_method', 'standard')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=cart.get_total_price(),
            delivery_method=delivery_method
        )
        
        # Add items to order
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        
        # Create initial delivery update
        DeliveryUpdate.objects.create(
            order=order,
            status='order_placed',
            description='Order has been placed successfully'
        )
        
        # Clear the cart
        cart.clear()
        
        messages.success(request, 'Order placed successfully')
        return redirect(ORDER_DETAIL_URL, order_id=order.id)
    
    return render(request, 'orders/order_create.html', {'cart': cart})

@login_required
def select_delivery_method(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow changing delivery method if order is still pending
    if order.status != 'pending':
        messages.error(request, 'Cannot change delivery method for orders that have been processed.')
        return redirect(ORDER_DETAIL_URL, order_id=order.id)
    
    if request.method == 'POST':
        form = DeliveryMethodForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.delivery_date = order.calculate_delivery_date()
            order.save()
            
            # Create a delivery update
            DeliveryUpdate.objects.create(
                order=order,
                status='order_placed',
                description=f'Order placed with {order.get_delivery_method_display()}'
            )
            
            messages.success(request, f'Delivery method updated to {order.get_delivery_method_display()}')
            return redirect(ORDER_DETAIL_URL, order_id=order.id)
    else:
        form = DeliveryMethodForm(instance=order)
    
    return render(request, 'orders/select_delivery_method.html', {
        'form': form,
        'order': order
    })

@login_required
def track_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery_updates = order.delivery_updates.all()
    
    # Calculate estimated delivery time remaining
    if order.delivery_date and order.status != 'delivered' and order.status != 'cancelled':
        today = timezone.now().date()
        days_remaining = (order.delivery_date - today).days
        if days_remaining < 0:
            days_remaining = 0
    else:
        days_remaining = 0
    
    return render(request, 'orders/track_delivery.html', {
        'order': order,
        'delivery_updates': delivery_updates,
        'days_remaining': days_remaining
    })
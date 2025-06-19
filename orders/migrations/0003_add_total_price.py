from django.db import migrations, models
from decimal import Decimal

def set_default_total_price(apps, schema_editor):
    order_model = apps.get_model('orders', 'Order')
    for order in order_model.objects.all():
        # Calculate total from order items if possible
        total = Decimal('0.00')
        for item in order.items.all():
            total += item.price * item.quantity
        
        # If no items or calculation is zero, set a default value
        if total == 0:
            total = Decimal('0.00')
            
        order.total_price = total
        order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_add_delivery_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_total_price, migrations.RunPython.noop),
    ]
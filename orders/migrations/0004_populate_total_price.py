from django.db import migrations
from decimal import Decimal

def set_default_total_price(apps, schema_editor):
    order_model = apps.get_model('orders', 'Order')
    # OrderItem is not used, so we don't need to import it
    
    for order in order_model.objects.all():
        # Set a default value for all existing orders
        order.total_price = Decimal('0.00')
        order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_add_total_price'),
    ]

    operations = [
        migrations.RunPython(set_default_total_price, migrations.RunPython.noop),
    ]
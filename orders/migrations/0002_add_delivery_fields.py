from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='updated',
            new_name='updated_at',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('standard', 'Standard Delivery (3-5 days)'), ('express', 'Express Delivery (1-2 days)'), ('same_day', 'Same Day Delivery')], default='standard', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='DeliveryUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('order_placed', 'Order Placed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('delayed', 'Delayed')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_updates', to='orders.order')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
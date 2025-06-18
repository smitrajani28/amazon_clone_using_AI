from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('delivery/<int:order_id>/', views.select_delivery_method, name='select_delivery_method'),
    path('track/<int:order_id>/', views.track_delivery, name='track_delivery'),
]
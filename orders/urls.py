from django.urls import path
from . import views

app_name ='orders'

urlpatterns = [
    path('place-orders/', views.place_order, name='place_order'),
    path('order-confirmation/<str:order_id>/',views.order_confirmation,name='order_confirmation')
    
]
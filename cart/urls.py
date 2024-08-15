
from django.urls import path, include
from . import views

app_name = 'cart'

urlpatterns = [
    
    path('cart/',views.cart_view,name='cart_view'),
    path('add-cart/',views.add_to_cart,name='add_to_cart'),
    path('update/<int:item_id>/',views.update_cart_item,name='update_cart_item'),
    path('remove/<int:item_id>/',views.remove_from_cart,name='remove_from_cart'), 
    path('cart/', views.cart_view, name='cart_view'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
]


    
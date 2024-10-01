from django.urls import path
from . import views

app_name ='userpanel'

urlpatterns = [
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('order/<str:order_id>/cancel/',views.cancel_order,name='cancel_order'),
    path('order/<str:order_id>/',views.order_detail,name='order_detail'),
    path('return-request/<str:order_id>/', views.return_request, name='return_request'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('remove-from-wishlist/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

]

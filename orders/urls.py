from django.urls import path
from . import views

app_name ='orders'

urlpatterns = [
    path('place-orders/', views.place_order, name='place_order'),
    path('order-confirmation/<str:order_id>/',views.order_confirmation,name='order_confirmation'),
    path('razorpay-payment/<str:order_id>/', views.razorpay_payment, name='razorpay_payment'),
    path('razorpay-callback/', views.razorpay_callback, name='razorpay_callback'),
    path('payment-failed/',views.payment_failed,name='payment_failed'),
    path('admin/order/list/', views.admin_order_list, name='admin-order-list'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/change-status/', views.change_order_status, name='change_order_status'),
]
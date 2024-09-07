from django.urls import path
from . import views

app_name ='coupon'

urlpatterns = [
    path('coupon-list/', views.coupon_list, name='coupon_list'),
    path('coupon-create/',views.create_coupon,name='create_coupon'),
    path('generate-code/',views.generate_coupon_code,name='generate_coupon_code'),
    path('edit-coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),
    path('toggle-coupon/<int:coupon_id>/',views.toggle_coupon,name='toggle_coupon'),
    path('apply-coupon/',views.apply_coupon,name='apply_coupon'),
    path('remove-coupon/',views.remove_coupon,name='remove_coupon'),
    
]

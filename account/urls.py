from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup, name ='signup'),
    path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('index/', views.index, name = 'index'),
    path('signout/', views.signout, name = 'signout'),
    
    
    
    
]

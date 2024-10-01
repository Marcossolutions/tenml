from django.urls import path, include
from . import views
from .views import CustomPasswordResetView,CustomPasswordResetDoneView,CustomPasswordRestConfirmView,CustomPasswordResetCompleteView
urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup, name ='signup'),
    path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('index/', views.index, name = 'index'),
    path('signout/', views.signout, name = 'signout'),
    path('password-reset/',CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/',CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',CustomPasswordRestConfirmView.as_view(),name='password_reset_confirm'),
    path('password-reset-complete/',CustomPasswordResetCompleteView.as_view(),name='password_reset_complete'),
    
    
]

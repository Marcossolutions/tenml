
from django.urls import path, include
from . import views


app_name='adminpanel'

urlpatterns = [
    
    path('admin-login/',views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name = 'admin_dashboard'),
    path('user-list/',views.user_list, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name= 'delete_user'),
    path('restore_user/<int:user_id>/', views.restore_user, name = 'restore_user'),
    path('admin-logout/',views.admin_logout,name='admin_logout'),
]


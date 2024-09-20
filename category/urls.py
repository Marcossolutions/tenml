
from django.urls import path, include
from . import views
from .views import UserCategoryListView

app_name = 'category'

urlpatterns = [
 
   
    path('category-list/', views.category_list, name ='category_list'),
    path('add-category', views.create_category, name = 'add-category'),
    path('edit-category/<int:category_id>/', views.edit_category, name = 'edit_category'),
    path('delete-category/<int:category_id>/',views.delete_category,name= 'delete_category'),
    path('toggle-category-listing/<int:category_id>/',views.toggle_category_listing, name = 'toggle_category_listing'),
    path('user-category-list/', UserCategoryListView.as_view(), name='user_category_list'),
    
]

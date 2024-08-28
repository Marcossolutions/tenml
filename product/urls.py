
from django.urls import path, include
from . import views

app_name ='product'

urlpatterns = [
    
   path('product-list',views.product_list,name='product_list'),
   path('create-product',views.create_product,name='create_product'),
   path('edit-product/<int:product_id>/', views.edit_product,name='edit_product'),
   path('detail/<int:product_id>/',views.product_detail,name='product_detail'),
   path('toggle/<int:product_id>/',views.toggle_product,name='toggle_product'),
   path('upload-images/<int:product_id>/', views.upload_product_images, name='upload_images'),
   path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
   path('product-detail-page/<int:product_id>/',views.product_detail_page,name='product_detail_page'),
   path('shop/', views.shop_page,name='shop_page'),
   path('search/', views.search_product,name='search_product'),
   path('product/<int:product_id>/variant/',views.variant_details,name = 'variant_details'),
   path('product/<int:product_id>/variant/create/',views.create_variant, name ='create_variant'),
   path('variant/<int:variant_id>/edit/',views.edit_variant, name ='edit_variant'),
   path('variant/<int:variant_id>/toggle/', views.toggle_variant_status, name = 'toggle_variant_status'),
   path('variant/<int:variant_id>/delete/', views.delete_variant, name = 'delete_variant'),
   path('variant/<int:variant_id>/restore/',views.restore_variant, name='restore_variant'),
   path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
   path('check-variant-in-cart/', views.check_variant_in_cart, name='check_variant_in_cart'),

]


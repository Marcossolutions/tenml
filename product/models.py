from django.db import models
from category.models import Category
from account.models import User

class Product(models.Model):
    product_name = models.CharField(max_length=100, null=False)
    product_decription = models.TextField(1000,null=False)
    product_category = models.ForeignKey(Category,on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    offer_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    thumbnail = models.ImageField(upload_to='thumbnail_image', null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.product_name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size =models.CharField(max_length=10,null=True)
    variant_price = models.DecimalField(max_digits=10,decimal_places=2)
    variant_stock =models.PositiveIntegerField(null=False,default=0)
    variant_status = models.BooleanField(default=True)
    
    
    def __str__(self) :
        return f'{self.size} -{self.product.product_name}'
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='images')
    images = models.ImageField(
        upload_to="product_images", default=r"E:\Brototype\ecom Project\tenml\static\adminside\assets\imgs\product_images\No image.jpg"
    )

    def __str__(self):
        return f"Image for {self.product.product_name}"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField( max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)    
    
    def str(self):
        return f'{self.user} - {self.product}'
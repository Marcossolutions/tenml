from django.db import models
from account.models import User
from product.models import Product ,ProductVariant

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cart for {self.user.username}'
    
    def get_total(self):
        return sum(item.get_total_price() for item in self.cartitems.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cartitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.quantity} x {self.product.product_name}'
    
    def get_total_price(self):
        return self.variant.get_discounted_amount() * self.quantity

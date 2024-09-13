from django.db import models
from account.models import User
from product.models import ProductVariant

class UserProfile(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username

class UserAddress(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=100, null=False)
    street_name = models.CharField(max_length=100, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    country = models.CharField(max_length=50, null=False, default="null")
    phone_number = models.CharField(max_length=50, null=False)
    status = models.BooleanField(default=False)
    is_deleted =models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.name},{self.house_name},{self.street_name},{self.district},{self.state},{self.country}'
    
    class Meta:
        
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
    
class Wallet(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    updated= models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f"{self.user.username}'s Wallet"
        
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
    ('CREDIT', 'Credit'),
    ('DEBIT', 'Debit'),
    )
        
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    transaction_type = models.CharField(max_length=6,choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)
        
    def __str__(self) -> str:
        return f"{self.transaction_type} of {self.amount} to {self.wallet.user.username}'s Wallet"    
    class Meta:
        ordering = ['-timestamp']
        
        
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together =('user','variant')
    
    def __str__(self):
        return f"{self.user.username}'s wishlist : {self.variant}"
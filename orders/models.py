from django.db import models
from account.models import User
from product.models import ProductVariant
from decimal import Decimal


class OrderAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50,null=False)
    house_name = models.CharField(max_length=100,null=False)
    street_name = models.CharField(max_length=100,null=False)
    district = models.CharField(max_length=50,null=False)
    state =models.CharField(max_length=50,null=False)
    country = models.CharField(max_length=50,null=False)
    pin_number = models.IntegerField(null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.name},{self.house_name},{self.street_name},{self.district},{self.country}'
    

class OrderMain(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Awaiting Payment','Awaiting Payment'),
        ('Confirmed','Confirmed'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Canceled','Canceled'),
        ('Returned','Returned'),
    ]
    PAYEMENT_METHOD_CHOICES = [
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Razorpay','Razorpay'),
        ('Wallet Payment','Wallet Payment'),
    ]
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL,null=True)
    total_amount = models.DecimalField(max_digits=15,decimal_places=2,null=False)
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    final_amount = models.DecimalField(max_digits=15,decimal_places=2)
    date = models.DateField(auto_now_add=True)
    order_status =models.CharField(max_length=100,choices=ORDER_STATUS_CHOICES,default='Pending')
    payment_method = models.CharField(max_length=50, choices=PAYEMENT_METHOD_CHOICES,default='Cash on Delivery')
    order_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50,blank=True,null=True)
    
    
    def __str__(self):
        return f'Order{self.order_id} by {self.user.username}'



class OrderSub(models.Model):
    main_order = models.ForeignKey(OrderMain,related_name='order_items',on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=False,default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False,default=0)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, null=True,blank=True)
    
    def total_cost(self):
        return Decimal(self.quantity) * Decimal(self.price) 
    
    def __str__(self):
        return f'{self.quantity} x {self.variant.product.product_name} ({self.variant.size})'
    
    
class ReturnRequest(models.Model):
    RETURN_STATUS_CHOICE=[
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    ]
    order = models.ForeignKey(OrderMain,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=15,choices=RETURN_STATUS_CHOICE,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Return request for Order{self.order.order_id}"
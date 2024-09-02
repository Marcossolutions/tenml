from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    coupon_name= models.CharField(max_length=100)
    coupon_code= models.CharField(max_length=50, unique=True)
    minimum_amount= models.IntegerField()
    discount = models.IntegerField()
    maximum_amount = models.IntegerField(default=0)
    expiry_date= models.DateField()
    status = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        return self.status and self.expiry_date>= timezone.now().date()



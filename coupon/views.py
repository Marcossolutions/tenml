from django.shortcuts import render, redirect,get_object_or_404
from .models import Coupon
from .forms import CouponForm
from django.contrib import messages
from django.http import JsonResponse
import string
import random

def coupon_list(request):
    coupons= Coupon.objects.all().order_by('-created_at')
    context= {'coupons':coupons}
    return render(request,'adminpart/coupon_list.html',context)

def create_coupon(request):
    if request.method =='POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Coupon created successfully.")
            return redirect('coupon:coupon_list')
    else:
        form=CouponForm()
    
    context= {'form':form, 'action':'Create'}
    return render(request, 'adminpart/create_coupon.html',context)

def generate_coupon_code(request):
    if request.method == 'GET':
        length=8
        characters = string.ascii_uppercase + string.digits
        coupon_code = ''.join(random.choice(characters) for _ in range(length))
        return JsonResponse({'coupon_code':coupon_code})
    
def edit_coupon(request,coupon_id):
    coupon= get_object_or_404(Coupon,id=coupon_id)
    if request.method=='POST':
        form=CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request,"Coupon edited successfully.")
            return redirect('coupon:coupon_list')
    else:
        form = CouponForm(instance=coupon)
    context={'form':form,'action':'edit'}
    return render(request,'adminpart/edit_coupon.html',context)
        

def toggle_coupon(request,coupon_id):
    coupon= get_object_or_404(Coupon,id=coupon_id)
    coupon.status = not coupon.status
    coupon.save()
    action= 'activated' if coupon.status else 'deactivated'
    messages.success(request,f'Coupon {action} succesfully.')
    return redirect('coupon:coupon_list')
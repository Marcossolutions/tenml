from django.shortcuts import render, redirect,get_object_or_404
from .models import Coupon ,UserCoupon
from .forms import CouponForm
from django.contrib import messages
from django.http import JsonResponse
import string
import random
from cart.models import CartItem
from django.views.decorators.http import require_POST
from adminpanel.decorators import admin_required


@admin_required
def coupon_list(request):
    coupons= Coupon.objects.all().order_by('-created_at')
    context= {'coupons':coupons}
    return render(request,'adminpart/coupon_list.html',context)

@admin_required
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

@admin_required
def generate_coupon_code(request):
    if request.method == 'GET':
        length=8
        characters = string.ascii_uppercase + string.digits
        coupon_code = ''.join(random.choice(characters) for _ in range(length))
        return JsonResponse({'coupon_code':coupon_code})

@admin_required    
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
        

@admin_required
def toggle_coupon(request,coupon_id):
    coupon= get_object_or_404(Coupon,id=coupon_id)
    coupon.status = not coupon.status
    coupon.save()
    action= 'activated' if coupon.status else 'deactivated'
    messages.success(request,f'Coupon {action} succesfully.')
    return redirect('coupon:coupon_list')




# user side

from django.http import JsonResponse
from decimal import Decimal
from django.utils import timezone
import json




def apply_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')
        
        # Ensure cart_total is in the session
        cart_total = request.session.get('cart_total')
        if cart_total is None:
            return JsonResponse({'success': False, 'message': 'Cart total is missing. Please try again.'}, status=400)

        # Convert cart_total to a float (if it is not already)
        cart_total = float(cart_total)

        # Find the coupon
        coupon = Coupon.objects.filter(coupon_code=coupon_code, status=True, expiry_date__gte=timezone.now()).first()
        if not coupon:
            return JsonResponse({'success': False, 'message': 'Invalid or expired coupon.'})

        # Check if the user has already redeemed this coupon
        if UserCoupon.objects.filter(user=request.user, coupon=coupon, redeemed=True).exists():
            return JsonResponse({'success': False, 'message': 'Coupon has already been used.'})

        # Calculate discount and total
        discount_amount = float((coupon.discount / 100) * cart_total)
        discounted_total = float(cart_total - discount_amount)

        # Save the coupon application in session
        request.session['applied_coupon'] = {
            'coupon_code': coupon.coupon_code,
            'discount_amount': discount_amount,
            'discounted_total': discounted_total,
        }

        return JsonResponse({'success': True, 'discount_amount': discount_amount, 'final_total': discounted_total})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



def remove_coupon(request):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        return JsonResponse({'success': True, 'message': 'Coupon removed successfully.'})
    return JsonResponse({'success': False, 'message': 'No coupon found to remove.'}, status=400)



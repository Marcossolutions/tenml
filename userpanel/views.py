from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import UserProfile,UserAddress, Wallet,WalletTransaction,Wishlist
from django.contrib.auth.decorators import login_required
from .forms import UserPofileForm,UserAddressForm,EditUserProfileForm,CustomPasswordChangeForm
from django.core.paginator import Paginator
from django.contrib import messages
from orders.models import OrderMain,OrderSub, ReturnRequest
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from product.models import ProductVariant
from django.http import JsonResponse
import json




@login_required(login_url='/login/')
def view_profile(request):
    user_profile,created = UserProfile.objects.get_or_create(user=request.user)
    
    addresses = UserAddress.objects.filter(user =request.user,is_deleted=False)
    addresses_count = addresses.count()
    address_paginator= Paginator(addresses,3)
    address_page = request.GET.get('address_page')
    paginated_addresses = address_paginator.get_page(address_page)
    
    orders= OrderMain.objects.filter(user= request.user).order_by('-id')
    orders_count= orders.count()
    order_paginator = Paginator(orders,3)
    order_page = request.GET.get('order_page')
    paginated_orders = order_paginator.get_page(order_page)
    
    for order in paginated_orders:
        order.items= OrderSub.objects.filter(main_order=order)
        
    wallet,_ = Wallet.objects.get_or_create(user=request.user)
    wallet_transactions= wallet.transactions.all()[:3]
    
    context = {
        'user':request.user,
        'user_profile':user_profile,
        'addresses':paginated_addresses,
        'orders':paginated_orders,
        'wallet':wallet,
        'wallet_transactions':wallet_transactions,
        'addresses_count':addresses_count,
        'orders_count':orders_count
    }
    return render(request,'userpart/user_interface/view_profile.html',context)

@login_required(login_url='/login/')
def edit_profile (request):
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = EditUserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request,"Your profile was successfully updated.")
                return redirect('userpanel:view_profile')
            
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user,request.POST)
            if password_form.is_valid():
                user=password_form.save()
                update_session_auth_hash(request,user)
                messages.success(request,"Youer password was successfully updated!")
                return redirect('userpanel:view_profile')
        
    
    form = EditUserProfileForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)
        
    return render(request,'userpart/user_interface/edit_profile.html',{'form':form, 'password_form':password_form})

@login_required(login_url='/login/')
def add_address(request):
    if request.method =='POST':
        form =UserAddressForm(request.POST)
        if form.is_valid():
            address= form.save(commit=False)
            address.user = request.user
            if address.status:
                UserAddress.objects.filter(user=request.user,status=True).update(status=False)
            address.save()
            return redirect('userpanel:view_profile')
    else:
        form = UserAddressForm()
    return render(request,'userpart/user_interface/add_address.html',{'form':form})

@login_required(login_url='/login/')
def edit_address(request,address_id):
    address = get_object_or_404(UserAddress,id =address_id,user = request.user)
    if request.method == 'POST':
        form = UserAddressForm(request.POST,instance =address)
        if form.is_valid():
            address =form.save(commit=False)
            if address.status:
                UserAddress.objects.filter(user=request.user, status =True).exclude(id=address.id).update(status=False)
            address.save()
            return redirect('userpanel:view_profile')
    else:
        form = UserAddressForm(instance=address)
    return render(request, 'userpart/user_interface/edit_address.html',{'form':form})

@login_required(login_url='/login/')
def delete_address(request,address_id):
    address = get_object_or_404(UserAddress,id=address_id,user=request.user)
    address.delete()
    return redirect ('userpanel:view_profile')

@login_required
def order_detail(request,order_id):
    order = get_object_or_404(OrderMain,id=order_id,user=request.user)
    order_items=OrderSub.objects.filter(main_order=order)
    
    context={
        'order':order,
        'order_items':order_items,
    }
    return render (request,'userpart/user_interface/order_details.html',context)

@login_required
def cancel_order(request,order_id):
    order = get_object_or_404(OrderMain,order_id=order_id,user=request.user)
    
    if order.order_status not in ['Pending','Confirmed','Shipped']:
        messages.error(request,"This order cannot be canceled at this stage.")
        return redirect ('userpanel:view_profile')
       
    if  order.payment_method=='Razorpay' or order.payment_method== 'wallet':
        
        wallet,created= Wallet.objects.get_or_create(user=request.user)
        wallet.balance += Decimal(order.final_amount)
        wallet.updated_at = timezone.now()
        wallet.save()
    
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=float(order.final_amount),
            description  =f"Refund for canceled order {order.order_id}",
            transaction_type='CREDIT'
            
        )
        
        order.order_status='Canceled'
        order.save()
        messages.success(request, f'Order {order.order_id} has been canceled and {order.final_amount} has been refunded to your wallet.')
    else:
        messages.success(request, f'Order {order.order_id} has been canceled successfully.')

    return redirect('userpanel:view_profile')


@login_required
def return_request(request,order_id):
    order = get_object_or_404(OrderMain, order_id=order_id, user=request.user)
    
    if order.order_status != 'Delivered':
        messages.error(request,'This order is not eligible for return.')
        return redirect('userpanel:view_profile')
    if ReturnRequest.objects.filter(order=order).exists():
        messages.error(request,'Return request for this order already exits.')
        return redirect('userpanel:view_profile')
    
    if request.method=='POST':
        reason =request.POST.get("reason")
        ReturnRequest.objects.create(
            order=order,
            user=request.user,
            reason=reason
        )
        order.order_status ='Return Requested'
        order.save()
        messages.success(request,"Return request has been submitted successfully.")
        return redirect('userpanel:order_detail',order_id=order.id)

    return render (request,'userpart/order/return_order.html',{'order':order})
    
@login_required
def wishlist(request):
    wishlist_items=Wishlist.objects.filter(user=request.user).select_related('variant')
    context = {'wishlist_items': wishlist_items}
    return render(request, 'userpart/user_interface/wishlist.html',context)

@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, variant=variant)
            if not created:
                wishlist_item.delete()
                return JsonResponse({'status': 'removed'})
            else:
                return JsonResponse({'status': 'added'})
        except ProductVariant.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Variant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
@login_required
def remove_from_wishlist(request):
    if request.method =='POST':
        wishlist_id = request.POST.get('wishlist_id')
        wishlist_item = get_object_or_404(Wishlist,id=wishlist_id,user=request.user)
        wishlist_item.delete()
        return redirect ('userpanel:wishlist')
        
    else:
        return redirect ('userpanel:wishlist')
    
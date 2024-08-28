from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import UserProfile,UserAddress
from django.contrib.auth.decorators import login_required
from .forms import UserPofileForm,UserAddressForm,EditUserProfileForm
from django.core.paginator import Paginator
from django.contrib import messages
from orders.models import OrderMain,OrderSub




@login_required(login_url='/login/')
def view_profile(request):
    user_profile,created = UserProfile.objects.get_or_create(user=request.user)
    addresses = UserAddress.objects.filter(user =request.user,is_deleted=False)
    address_paginator= Paginator(addresses,3)
    address_page = request.GET.get('address_page')
    paginated_addresses = address_paginator.get_page(address_page)
    
    orders= OrderMain.objects.filter(user= request.user).order_by('-date')
    order_paginator = Paginator(orders,5)
    order_page = request.GET.get('order_page')
    paginated_orders = order_paginator.get_page(order_page)
    for order in paginated_orders:
        order.items= OrderSub.objects.filter(main_order=order)
    context = {
        'user':request.user,
        'user_profile':user_profile,
        'addresses':paginated_addresses,
        'orders':paginated_orders
    }
    return render(request,'userpart/user_interface/view_profile.html',context)

@login_required(login_url='/login/')
def edit_profile (request):
    
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect ('userpanel:view_profile')
    else:
        form = EditUserProfileForm(instance=request.user)
    return render(request,'userpart/user_interface/edit_profile.html',{'form':form})

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

def cancel_order(request,order_id):
    order = get_object_or_404(OrderMain,order_id,user=request.user)
    
    if order.order_status !='Pending':
        messages.error(request,"This order cannot be canceled.")
        return redirect ('userpanel:view_profile')
    
    order.order_status = 'Canceled'
    order.save()
    
    order_items = OrderSub.objects.filter(main_order=order)
    for item in order_items:
        item.variant.variant_stock += item.quantity
        item.variant.save()
    
    messages.success(request,"Your order has been successfully canceled.")
    return redirect('userpanel:veiw_profile')
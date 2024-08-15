from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import UserProfile,UserAddress
from django.contrib.auth.decorators import login_required
from .forms import UserPofileForm,UserAddressForm,EditUserProfileForm




@login_required(login_url='/login/')
def view_profile(request):
    user_profile,created = UserProfile.objects.get_or_create(user=request.user)
    addresses = UserAddress.objects.filter(user =request.user)
    context = {
        'user_profile':user_profile,
        'addresses':addresses
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

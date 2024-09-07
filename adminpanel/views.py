from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from account.forms import loginform
from account.models import User



def admin_login(request):
    if request.method == 'POST':
        form = loginform(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email,password=password)
        
            if user is not None:
                if user.is_admin:
                    login(request, user)
                    return redirect ('adminpanel:admin_dashboard')
                else:
                    messages.error(request,'You are not a authorized to access this page.')
            else:
                messages.error(request,'Invalid email or password')
    else:
        form = loginform()
    
    return render(request,'adminpart/admin_login.html', {'form': form})


def admin_logout(request):
    logout(request)
    return redirect('adminpanel:admin_login')


def admin_dashboard(request):
    return render(request, 'adminpart/index-dark.html')

def user_list(request):
    users=User.objects.filter(is_admin=False)
    print('clicked')
    return render(request,'adminpart/users-list.html', {'users':users})

def delete_user(request,user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method =='POST':
        user.is_active = False
        user.save()
        return redirect('adminpanel:user_list')
    return render (request, 'adminpart/delete_user_confirmation..html', {'user':user})

def restore_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
        return redirect('adminpanel:user_list')
    return render (request, 'adminpanel/restore_user_confirmation.html', {'user':user})
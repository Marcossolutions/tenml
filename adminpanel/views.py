from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from account.forms import loginform
from account.models import User
from orders.models import OrderMain
from django.utils.timezone import timedelta 
from datetime import timedelta ,datetime
from django.db.models import Sum, Count, F, Q
from django.utils import timezone



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

def sales_report(request):
    filter_type = request.GET.get('filter', None)
    now = timezone.now()
    start_date = end_date = None 

    if filter_type == 'weekly':
        start_date = now - timedelta(days=now.weekday())
        end_date = now
    elif filter_type == 'monthly':
        start_date = now.replace(day=1)
        end_date = now

    if start_date and end_date:
        orders = OrderMain.objects.filter(
            order_status="Delivered",
            is_active=True,
            date__range=[start_date, end_date]
        )
    else:
        orders = OrderMain.objects.filter(
            order_status="Delivered",
            is_active=True
        )

    total_discount = orders.aggregate(total=Sum('discount_amount'))['total'] or 0
    total_orders = orders.aggregate(total=Count('id'))['total'] or 0
    total_order_amount = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request, 'adminpart/salesreport.html', {
        'orders': orders,
        'total_discount': total_discount,
        'total_orders': total_orders,
        'total_order_amount': total_order_amount
    })

def order_date_filter(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return redirect('sales-report')

            orders = OrderMain.objects.filter(date__range=[start_date, end_date], order_status="Delivered")
            total_discount = orders.aggregate(total=Sum('discount_amount'))['total'] or 0
            total_orders = orders.aggregate(total=Count('id'))['total'] or 0
            total_order_amount = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            return render(request, 'adminpart/salesreport.html', {
                'orders': orders,
                'total_discount': total_discount,
                'total_orders': total_orders,
                'total_order_amount': total_order_amount,
            })

    return redirect('sales-report')

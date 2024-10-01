from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect, get_object_or_404,render
from django.contrib import messages
from account.forms import loginform
from account.models import User
from orders.models import OrderMain,OrderSub
from django.utils.timezone import timedelta 
from datetime import timedelta ,datetime
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay, TruncDate
from product.models import Product, ProductVariant
from category.models import Category
from .decorators import admin_required




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



@admin_required
def admin_dashboard(request):
    # Basic metrics
    total_revenue = OrderMain.objects.filter(payment_status=True).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    total_orders = OrderMain.objects.exclude(order_status='Canceled').count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()

    # Monthly earnings
    current_month = timezone.now().month
    monthly_earnings = OrderMain.objects.filter(
        payment_status=True,
        date__month=current_month
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0

    # Yearly sales data
    current_year = timezone.now().year
    yearly_sales = (OrderMain.objects.filter(payment_status=True, date__year=current_year)
                    .annotate(month=TruncMonth('date'))
                    .values('month')
                    .annotate(total_sales=Sum('final_amount'))
                    .order_by('month'))

    # Total sales and average order value
    total_sales = OrderMain.objects.filter(payment_status=True).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    avg_order_value = OrderMain.objects.filter(payment_status=True).aggregate(Avg('final_amount'))['final_amount__avg'] or 0

    # Latest orders
    latest_orders = OrderMain.objects.order_by('-date')[:10]

    # Top 10 best-selling products with categories
    best_selling_products = (OrderSub.objects
                             .values('variant__product__product_name', 'variant__product__product_category__category_name')
                             .annotate(total_sold=Sum('quantity'))
                             .order_by('-total_sold')[:10])

    # Top 10 best-selling categories
    best_selling_categories = (OrderSub.objects
                               .values('variant__product__product_category__category_name')
                               .annotate(total_sold=Sum('quantity'))
                               .order_by('-total_sold')[:10])

    # Prepare data for yearly sales chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    yearly_sales_data = [0] * 12
    for sale in yearly_sales:
        month_index = sale['month'].month - 1
        yearly_sales_data[month_index] = float(sale['total_sales'])

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        'monthly_earnings': monthly_earnings,
        'total_sales': total_sales,
        'avg_order_value': round(avg_order_value, 2),
        'latest_orders': latest_orders,
        'best_selling_products': best_selling_products,
        'best_selling_categories': best_selling_categories,
        'yearly_sales_labels': months,
        'yearly_sales_data': yearly_sales_data,
    }

    return render(request, 'adminpart/index-dark.html', context)
@admin_required
def user_list(request):
    users = User.objects.filter(is_admin=False).order_by('id')
    
    # Number of users per page
    per_page = 10
    
    paginator = Paginator(users, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'adminpart/users-list.html', {'page_obj': page_obj})
@admin_required
def delete_user(request,user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method =='POST':
        user.is_active = False
        user.save()
        return redirect('adminpanel:user_list')
    return render (request, 'adminpart/delete_user_confirmation..html', {'user':user})

@admin_required
def restore_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
        return redirect('adminpanel:user_list')
    return render (request, 'adminpanel/restore_user_confirmation.html', {'user':user})
@admin_required
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

    per_page = 10
    paginator = Paginator(orders, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminpart/salesreport.html', {
        'page_obj': page_obj,
        'total_discount': total_discount,
        'total_orders': total_orders,
        'total_order_amount': total_order_amount
    })
    
@admin_required
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

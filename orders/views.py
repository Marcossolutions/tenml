from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.contrib import messages
from userpanel.models import UserAddress,Wallet,WalletTransaction
from cart.models import CartItem
from decimal import Decimal
from django.urls import reverse
from .models import OrderAddress,OrderMain,OrderSub
import uuid
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
# Create your views here.



@login_required
def place_order(request):
    if request.method !='POST':
        return redirect('cart:checkout')
    
    
    user  = request.user
    cart_item_ids = request.POST.get('cart_item_ids','').split(',')
    address_id = request.POST.get('address_id')
    payment_method= request.POST.get('payment_method')
    
    if not cart_item_ids or not address_id or not payment_method:
        messages.error(request,"Invalid order data. Please try again.")
        return redirect('cart:checkout')
    
    try :
        user_address = UserAddress.objects.get(id=address_id,user = user)
    except UserAddress.DoesNotExist:
        messages.error (request,"Selected address is invalid.")
        return redirect('cart:checkout')
    
    order_address = OrderAddress.objects.create(
        user = user,
        name = user_address.name,
        house_name = user_address.house_name,
        street_name = user_address.street_name,
        district = user_address.district,
        state = user_address.state,
        country = user_address.country,
        pin_number = user_address.pin_number
    )
    
    cart_items = CartItem.objects.filter(id__in =cart_item_ids,cart__user=user)
    
    if not cart_items.exists():
        messages.error(request,"No valid items found in cart. Please try again.")
        return redirect('cart:checkout')
    
    cart_total = sum(item.get_total_price() for item in cart_items )
    discount_amount = Decimal('0.00')
    
    final_amount = cart_total-discount_amount
    
    order = OrderMain.objects.create(
        user = user,
        address = order_address,
        total_amount= cart_total,
        discount_amount = discount_amount,
        final_amount = final_amount,
        payment_method = payment_method,
        order_id = str(uuid.uuid4())[:10],
        order_status = 'Pending' if payment_method == 'Cash on Delivery' else 'Awaiting Payment'
    )
    
    for item in cart_items:
        OrderSub.objects.create(
            main_order = order,
            variant = item.variant,
            quantity = item.quantity,
            price = item.variant.variant_price
            
        )
        item.variant.variant_stock -= item.quantity
        item.variant.save()
        cart_items.delete()
    
    if payment_method == 'Razorpay':
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment_data = {
            'amount':int(final_amount*100),
            'currency':'INR',
            'receipt':order.order_id,
            'payment_capture':'1'
        }
        razorpay_order = client.order.create(data=payment_data)
        order.payment_id = razorpay_order['id']
        order.save()
        
        return redirect('orders:razorpay_payment',order_id = order.order_id)
    
    messages.success(request,"Order placed successfully!")
    return redirect('orders:order_confirmation',order_id =order.order_id)

@login_required
def order_confirmation(request,order_id):
    order = get_object_or_404(OrderMain,order_id=order_id,user=request.user)
    context = {
        'order':order,
    }
    return render(request,'userpart/order/order_confirmation.html',context)

@login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(OrderMain, order_id=order_id, user=request.user)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))   
    context = {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': order.payment_id,
        'callback_url': request.build_absolute_uri(reverse('orders:razorpay_callback'))
    }
    return render(request, 'userpart/order/razorpay_payment.html', context)

def razorpay_callback(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    if request.method == 'GET':
        params_dict = {
            'razorpay_payment_id': request.GET.get('razorpay_payment_id'),
            'razorpay_order_id': request.GET.get('razorpay_order_id'),
            'razorpay_signature': request.GET.get('razorpay_signature')
        }
    else:
        params_dict = {
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
        }
    try:      
        client.utility.verify_payment_signature(params_dict)
        order = OrderMain.objects.get(payment_id=params_dict['razorpay_order_id'])
        order.payment_status = True
        order.order_status = 'Confirmed'
        order.save()
        return redirect('orders:order_confirmation',order_id=order.order_id)
    except razorpay.errors.SignatureVerificationError:
       
        return redirect('orders:payment_failed')
    
    except Exception as e:
        
        print(f"An error occurred: {str(e)}")
        return redirect('orders:payment_failed')
    
@login_required 
def payment_failed(request):
    return render(request,'userpart/order/payment_failed.html')






 # Admin side order maniulation and listing
@staff_member_required
def admin_order_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'Show all')
    items_per_page = request.GET.get('items_per_page', 10)

    
    orders = OrderMain.objects.all().order_by('-id')
    
    if search_query:
        orders = orders.filter(order_id__icontains=search_query)
    if status_filter != 'Show all':
        orders = orders.filter(order_status=status_filter)

    
    paginator = Paginator(orders, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'items_per_page': items_per_page,
        'ORDER_STATUS_CHOICES': OrderMain.ORDER_STATUS_CHOICES,
    }
    return render(request, 'adminpart/admin_order_list.html', context)

def admin_order_detail(request,order_id):
    order = get_object_or_404(OrderMain,id=order_id)
    order_items = OrderSub.objects.filter(main_order=order)
    context ={
        'order':order,
        'order_items':order_items,
        'ORDER_STATUS_CHOICES':OrderMain.ORDER_STATUS_CHOICES,
    }
    return render(request,'adminpart/admin_order_detail.html', context)

def change_order_status(request,order_id):
    order =get_object_or_404(OrderMain,id=order_id)
    if request.method == 'POST':
        new_status=request.POST.get('order_status')
        current_status=order.order_status
        invalid_transitions={
            'Awaiting payment':['Pending'],
            'Confirmed':['Pending', 'Awaiting payment'],
            'Shipped': ['Confirmed','Awaiting payment', 'Pending'],
            'Delivered':['Shipped','Confirmed','Awaiting payment','Pending'],
            'Canceled':[status for status, _ in OrderMain.ORDER_STATUS_CHOICES],
            'Returned':[status for status, _ in OrderMain.ORDER_STATUS_CHOICES]
        }
        if new_status == 'Returned':
            messages.error(request,'Order status cannot be changed to Returned directly by the admin.')
        elif current_status in invalid_transitions and new_status in invalid_transitions[current_status]:
            messages.error(request,f'Cannot change status from{current_status} to {new_status}.')
        elif current_status == 'Delivered':
            messages.error(request, 'Cannot change status of a delivered order.')
        else:
            order.order_status = new_status
            if new_status == 'Delivered' and not order.payment_status:
                order.payment_status = True
            if new_status == 'Canceled' and order.payment_status:
                refund_amount = order.final_amount
                if order.payment_method == 'Razorpay' or order.payment_method =='wallet':       
                    wallet, created =Wallet.objects.get_or_create(user=order.user)
                    wallet.balance += Decimal(refund_amount)
                    wallet.updated = timezone.now()
                    wallet.save()
                    
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=float(refund_amount),
                        description=f"Refund for canceled order{order.order_id}",
                        transaction_type='CREDIT'
                    )
                    messages.success(request, f'Order {order.order_id} has been canceled and {refund_amount} has been refunded to the user\'s wallet.')
                else:
                    messages.success(request, f'Order {order.order_id} has been canceled successfully.')
                
                order.payment_status = False
                
            order.save()
            messages.success(request,'Order status updated successfully.')
            
    return redirect('orders:admin_order_detail',order_id=order.id)
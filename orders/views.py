from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from userpanel.models import UserAddress
from cart.models import CartItem
from decimal import Decimal
from .models import OrderAddress,OrderMain,OrderSub
import uuid
from django.contrib.auth.decorators import login_required
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
        
    
    
    messages.success(request,"Order placed successfully!")
    return redirect('orders:order_confirmation',order_id =order.order_id)

@login_required
def order_confirmation(request,order_id):
    order = get_object_or_404(OrderMain,order_id=order_id,user=request.user)
    context = {
        'order':order,
    }
    return render(request,'userpart/order/order_confirmation.html',context)
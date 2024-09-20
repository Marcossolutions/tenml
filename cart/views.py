from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem 
from product.models import Product
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Product, ProductVariant
import logging
from django.contrib import messages
from userpanel.models import UserAddress
from decimal import Decimal
from userpanel.forms import UserAddressForm
from coupon.models import Coupon ,UserCoupon
from django.utils import timezone

@login_required(login_url='/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'variant')
    cart_total = sum(item.get_total_price() for item in cart_items if item.variant.variant_stock > 0)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'userpart/cart/cart_view.html', context)



@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
            variant = ProductVariant.objects.get(id=variant_id, product=product)
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid product or variant.'}, status=400)

        if quantity > variant.variant_stock:
            return JsonResponse({'status': 'error', 'message': 'Not enough stock available.'}, status=400)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > variant.variant_stock:
                cart_item.quantity = variant.variant_stock
            cart_item.save()

        return JsonResponse({'status': 'success', 'message': 'Item added to cart.', 'cart_total': cart.get_total()})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required(login_url='/login/')
def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # Limit the quantity to the stock or 5, whichever is lower
        max_quantity = min(cart_item.variant.variant_stock, 5)
        if quantity > max_quantity:
            return JsonResponse({'success': False, 'error': f'Maximum quantity allowed is {max_quantity}.'})
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'item_total_price': cart_item.get_total_price(),
            'cart_total': cart_item.cart.get_total()
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        cart_total = cart_item.cart.get_total()

        messages.success(request, "Item removed from cart successfully.")
        return redirect('cart:cart_view')  # Redirect to the cart view page or any other page you wish

    except Exception as e:
        logger.error(f"Error removing item from cart: {str(e)}")
        messages.error(request, f"Failed to remove item from cart: {str(e)}")
        return redirect('cart:cart_view') 

def clear_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart.cartitems.all().delete()
    return redirect('cart:cart_view')



@login_required
def checkout(request):
    user = request.user
    cart_item_ids = request.GET.get('cart_items', '')
    user_addresses = UserAddress.objects.filter(user=user)
    
    if not cart_item_ids:
        messages.error(request, "Cash on Delivery is not available for orders above Rs 1000. Please choose a different payment method.")
        return redirect('cart:cart_view')
    
    cart_item_ids = cart_item_ids.split(',')
    cart_items = CartItem.objects.filter(id__in=cart_item_ids, cart__user=user)
    
    if not cart_items.exists():
        messages.error(request, "No valid items found in cart. Please try again.")
        return redirect('cart:cart_view')
    
    # Check stock and availability
    for item in cart_items:
        if item.quantity > item.variant.variant_stock:
            messages.error(request, f"Insufficient stock for {item.product.product_name}.")
            return redirect('cart:cart_view')
        if not item.product.is_active or not item.variant.variant_status:
            messages.error(request, f"{item.product.product_name} is no longer available.")
            return redirect('cart:cart_view')
    
    # If all checks pass, proceed to checkout
    cart_total = sum(item.get_total_price() for item in cart_items)
    
    # Store cart_total in session
    request.session['cart_total'] = float(cart_total)

    # Get available coupons
    available_coupons = Coupon.objects.filter(
        status=True,
        expiry_date__gte=timezone.now().date(),
        minimum_amount__lte=cart_total
    ).exclude(
        usercoupon__user=user,
        usercoupon__redeemed=True
    )
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'user_addresses': user_addresses,
        'available_coupons': available_coupons,
        'cart_item_ids': ','.join(map(str, cart_items.values_list('id', flat=True))),
    }
    
    return render(request, 'userpart/cart/checkout.html', context)


@login_required(login_url='/login/')
def add_address_checkout(request):
    if request.method =='POST':
        form =UserAddressForm(request.POST)
        if form.is_valid():
            address= form.save(commit=False)
            address.user = request.user
            if address.status:
                UserAddress.objects.filter(user=request.user,status=True).update(status=False)
            address.save()
            return redirect('cart:checkout')
    else:
        form = UserAddressForm()
    return render(request,'userpart/user_interface/add_address.html',{'form':form})
























# def checkout(request):
#     cart = get_object_or_404(Cart, user=request.user)
#     addresses = UserAddress.objects.filter(user=request.user, is_deleted=False)

#     if request.method == 'POST':
#         selected_item_ids = request.POST.getlist('selected_items[]')
        
#         selected_cart_items = CartItem.objects.filter(cart=cart, id__in=selected_item_ids)
        
#         selected_total = sum(item.get_total_price() for item in selected_cart_items)
        
  
#         cart.save()  # This will trigger the recalculation of cart total
        
#         return JsonResponse({
#             'success': True, 
#             'message': 'Checkout successful',
#             'new_cart_total': cart.get_total()
#         })

#     cart_items = cart.cartitems.all()
#     cart_total = cart.get_total()

#     context = {
#         'cart': cart,
#         'cart_items': cart_items,
#         'addresses': addresses,
#         'cart_total': cart_total,
#     }
#     return render(request, 'userpart/cart/checkout.html', context)



















































































# @login_required(login_url='/login/')
# def cart_view(request):
#     try:
#         cart = Cart.objects.get(user=request.user)
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(user = request.user)
        
#     cart_items= CartItem.objects.filter(cart=cart)
    
#     for item in cart_items:
#         item.item_total =item.product.price * item.quantity
        
#     total_price = sum(item.item_total for item in cart_items)   
    
#     context = {
#         'cart':cart,
#         'cart_items':cart_items,
#         'total_price':total_price
#         }
    
#     return render(request, 'userpart/cart/cart_view.html', context)

# @login_required(login_url='/login/')
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, _ = Cart.objects.get_or_create(user=request.user)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()

#     return JsonResponse({'status': 'success', 'quantity': cart_item.quantity})


# def update_cart_item(request,item_id):
#     cart_item = get_object_or_404(CartItem,id =item_id, cart__user=request.user)
#     if request.method =='POST':
#         quantity =request.POST.get('quantity')
#         if int (quantity)>0:
#             cart_item.quantity = int(quantity)
#             cart_item.save()
#         else:
#             cart_item.delete()
    
#     return redirect ('cart:cart_view')


# def remove_from_cart(request,cart_item_id):
#     cart_item = get_object_or_404(CartItem,id=cart_item_id, cart__user =request.user)
#     cart_item.delete()
#     return redirect ('cart:cart_view')

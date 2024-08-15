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

@login_required(login_url='/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(is_active=True,cart=cart)
    cart_total = cart.get_total()
    return render(request, 'userpart/cart/cart_view.html', {'cart_items': cart_items, 'cart_total': cart_total})




@login_required(login_url='/login/')
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please log in to add items to cart.'}, status=400)

    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id, product=product)
    except (Product.DoesNotExist, ProductVariant.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Invalid product or variant.'}, status=400)

    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({'status': 'success', 'message': 'Item added to cart.'})

@login_required(login_url='/login/')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0 and quantity <= 5:
        cart_item.quantity = quantity
        cart_item.save()
        item_total_price = cart_item.get_total_price()
        cart_total = cart_item.cart.get_total()
        return JsonResponse({'success': True, 'item_total_price': item_total_price, 'cart_total': cart_total})
    return JsonResponse({'success': False, 'error': 'Invalid quantity'})

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

def checkout(request):
    # Implement your checkout logic here
    return render(request, 'cart/checkout.html')

def checkout(request):
    try :
        cart = Cart.objects.get(user=request.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total =sum(item.get_total_price() for item in cart_items)
        
        context = {
            'cart_items':cart_items,
            'cart_total':cart_total,
        }
        return render(request, 'cart/checkout.html', context)
    except Cart.DoesNotExist:
        return redirect('cart:view_cart')


def checkout(request):

    cart = get_object_or_404(Cart, user=request.user)

    addresses = UserAddress.objects.filter(user=request.user, is_deleted=False)

    context = {
        'cart': cart,
        'cart_items': cart.cartitems.all(), 
        'addresses': addresses,
        'cart_total': cart.get_total(), 
    }
    return render(request, 'userpart/cart/checkout.html', context)





















































































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

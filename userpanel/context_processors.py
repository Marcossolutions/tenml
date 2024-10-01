# context_processors.py

from cart.models import CartItem, Cart
from userpanel.models import Wishlist

def cart_and_wishlist_count(request):
    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        # Get Cart count
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart, is_active=True).count()

        # Get Wishlist count
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count
    }

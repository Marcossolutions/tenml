from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product ,ProductImage, Category ,Review,ProductVariant
from .forms import Productform,ProductVariantForm
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from cart.models import CartItem,Cart
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import Productform



def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    return render(request, 'adminpart/product_list.html', context)



def create_product(request):
    if request.method == 'POST':
        form = Productform(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product:upload_images', product_id=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = Productform()
    
    context = {
        'form': form,
    }
    return render(request, 'adminpart/product_create.html', context)


def upload_product_images(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        files = request.FILES.getlist('images')
        for f in files:
            ProductImage.objects.create(product=product, images=f)
        messages.success(request, 'Images uploaded successfully.')
        return redirect('product:product_detail', product_id=product.id)

    context = {'product': product}
    return render(request, 'adminpart/product_image_upload.html', context)

def delete_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    image.delete()
    messages.success(request, 'Image deleted successfully.')
    return redirect('product:product_detail', product_id=product_id)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = Productform(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product=form.save(commit=False)
            if product.offer_price is None:
                product.offer_price =0.0
            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product:product_list')
    else:
        form = Productform(instance=product)
    
    context = {'form': form,'product': product}
    return render(request, 'adminpart/product_edit.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    variants = ProductVariant.objects.filter(product=product)
    default_price = variants.first().variant_price if variants.exists() else product.price
    
    for variant in variants:
        variant.discounted_amount=variant.get_discounted_amount()
    context = {
        'product': product,
        'product_images': product_images,
        'variants': variants,
        'default_price' : default_price
    }
    return render(request, 'adminpart/product_detail.html', context)


def toggle_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.is_active = not product.is_active
        product.save()
        status = 'activated' if product.is_active else 'deactivated'
        messages.success(request, f'Product {status} successfully.')
    return redirect('product:product_list')




def create_variant(request,product_id):
    product = get_object_or_404(Product, id =product_id)
    
    if  request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            messages.success(request,'Variant added successfully.')
            return redirect('product:variant_details',product_id = product.id)
    else:
        form = ProductVariantForm()
        
    context = {
        'form':form,
        'product':product
    }
    return render(request,'adminpart/variant/create_variant.html',context)

def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id= variant_id)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance = variant)
        if form.is_valid():
            form.save()
            messages.success(request,'Variant updated successfully.')
            return redirect ('product:variant_details', product_id = variant.product.id)
        
    else:
        form = ProductVariantForm(instance=variant)
        
    return render(request,'adminpart/variant/edit_variant.html', {'form':form,'variant':variant})    
    

def variant_details(request,product_id):
    product = get_object_or_404(Product,id =product_id)
    
    variants = ProductVariant.objects.filter(product=product)
    context = {
        'product': product,
        'variants':variants
    }
    
    return render (request, 'adminpart/variant/variant_details.html',context)

def toggle_variant_status(request,variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.variant_status = not variant.variant_status
    variant.save()
    status = 'deactivated' if variant.variant_status else 'activated'
    messages.success(request,f'Variant {status} successfully.')
    return redirect('product:variant_details', product_id=variant.product.id)

def delete_variant(request,variant_id):
    variant = get_object_or_404(ProductVariant,id = variant_id)
    variant.variant_status = False
    variant.save()
    messages.success(request, 'Variant deleted successfully.')
    return redirect('product:variant_details', product_id = variant.product.id)


def restore_variant(request,variant_id):
    variant = get_object_or_404(ProductVariant, id = variant_id)
    variant.variant_status = True
    variant.save()
    messages.success(request, 'Variant restored successfully.')
    return redirect('product:variant_details', product_id = variant.product.id)

    
    


#user side product fuctions


# def product_detail_page(request, product_id):
#     product = get_object_or_404(Product, id=product_id, is_active=True)
#     product_images = product.images.all()  
#     product_variants = ProductVariant.objects.filter(product=product)
#     context = {
#         'product': product,
#         'product_images': product_images,
#         'product_variants':product_variants,
#     }
#     return render(request, 'userpart/user_panel/shop_product-detail.html', context)


def product_detail_page(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    product_images = product.images.all()
    product_variants = ProductVariant.objects.filter(product=product)
    selected_variant = product_variants.first() if product_variants.exists() else None

    in_cart = False
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            in_cart = CartItem.objects.filter(cart=cart, product=product).exists()
        except Cart.DoesNotExist:
            pass
        
    context = {
        'product': product,
        'product_images': product_images,
        'product_variants': product_variants,
        'selected_variant': selected_variant,
        'in_cart' : in_cart
    }

    return render(request, 'userpart/user_panel/shop_product-detail.html', context)


@login_required(login_url='/login/')
def check_variant_in_cart(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            cart = Cart.objects.get(user=request.user)
            in_cart = CartItem.objects.filter(cart=cart, variant=variant).exists()
            return JsonResponse({'status': 'success', 'in_cart': in_cart})
        except ProductVariant.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid variant.'}, status=400)
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'success', 'in_cart': False})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


# def check_variant_in_cart(request):
#     variant_id = request.GET.get('variant_id')
#     if not variant_id:
#         return JsonResponse({'error': 'Variant ID is required'}, status=400)

#     # Assuming you have a Cart model and CartItem model
#     variant = get_object_or_404(ProductVariant, id=variant_id)
#     cart_item_exists = CartItem.objects.filter(cart__user=request.user, variant=variant, is_active=True).exists()

#     if cart_item_exists:
#         return JsonResponse({'in_cart': True})
#     else:
#         return JsonResponse({'in_cart': False})

from django.db.models import Prefetch, Min, Max
from decimal import Decimal

def shop_page(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).prefetch_related(
        Prefetch('productvariant_set', queryset=ProductVariant.objects.filter(variant_status=True))
    )

    search_query = request.GET.get('search_query', '')
    selected_categories = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_query:
        products = products.filter(Q(product_name__icontains=search_query) | Q(product_decription__icontains=search_query))

    if selected_categories:
        products = products.filter(product_category__id__in=selected_categories)

    if min_price:
        min_price = Decimal(min_price)
        products = products.annotate(min_variant_price=Min('productvariant__variant_price')).filter(
            Q(min_variant_price__gte=min_price) | Q(price__gte=min_price)
        )

    if max_price:
        max_price = Decimal(max_price)
        products = products.annotate(max_variant_price=Max('productvariant__variant_price')).filter(
            Q(max_variant_price__lte=max_price) | Q(price__lte=max_price)
        )

    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price_low_high':
        products = products.annotate(min_price=Min('productvariant__variant_price')).order_by('min_price', 'price')
    elif sort_by == 'price_high_low':
        products = products.annotate(max_price=Max('productvariant__variant_price')).order_by('-max_price', '-price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created_at')
    elif sort_by == 'name_az':
        products = products.order_by('product_name')
    elif sort_by == 'name_za':
        products = products.order_by('-product_name')

    context = {
        'categories': categories,
        'products': products,
        'current_sort': sort_by,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
    }

    return render(request, 'userpart/user_panel/shop_page.html', context)


def search_product(request):
    search_query= request.GET.get('q'),
    products = Product.objects.filter(is_active=True)
    
    if search_query:
        print(f'Search query:{search_query}')
        products = products.filter(Q(product_name__iexact=search_query) | 
                                   Q(product_decription__iexact=search_query))
        print(f'Filtered product:{products.count()}')
    context = {
        'products': products,
        'search_query' : search_query
    }
    return render(request, 'userpart/user_panel/shop_page.html', context)




@login_required
@require_POST
def submit_review(request, product_id):
    if request.is_ajax():
        user = request.user
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('review')
        
        review = Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({
            'user': review.user.username,
            'created_at': review.created_at.strftime('%b %d, %Y'),
            'rating': review.rating,
            'comment': review.comment,
            'rating_percentage': (review.rating / 5) * 100
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)






























































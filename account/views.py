
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, OTPForm, loginform
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.contrib.auth import authenticate, login ,logout
from product.models import Product ,ProductImage, Category
from django.core.exceptions import ObjectDoesNotExist
from .signals import user_registered

def index(request):
    return render(request,'userpart/user_panel/index.html')


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():

            request.session['user_data'] = form.cleaned_data

            user_registered.send(
                sender=None, 
                user=form.cleaned_data, 
                request=request
            )
            
            return redirect('verify_otp')
    else:
        if 'user_data ' in request.session:
            del request.session['user_data']
        form = UserRegistrationForm()
       
    storage =messages.get_messages(request)
    storage.used = True
    return render(request, 'userpart/user_panel/signup_page.html', {'form': form})


def verify_otp(request):
    if request.method=='POST' :
        form = OTPForm (request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            session_otp = request.session.get('otp')
            otp_generation_time = request.session.get('otp_generation_time')
            otp_age = timezone.now() - timezone.datetime.fromisoformat(otp_generation_time)
            
            if entered_otp == session_otp and otp_age.total_seconds()<120:
                user_data = request.session.get('user_data')
                
                user = User(
                    username = user_data['username'],
                    email = user_data['email'],
                    phone_number = user_data ['phone_number']
                )
                user.set_password(user_data['password'])
                user.is_active = True
                user.save()
                
                del request.session['otp']
                del request.session['otp_generation_time']
                del request.session['user_data']
                
                messages.success(request,'Account created succesfully')
                return redirect ('login_page')
            else:
                form.add_error(None, 'Invalid OTP or OTP has expired')
    else:
        form = OTPForm()
    return render (request,'userpart/user_panel/verify_otp.html', {'form':form})

def resend_otp(request):
    user_data = request.session.get('user_data')
    if user_data:
        otp = get_random_string(length=6,allowed_chars='1234567890')
        print(otp)
        otp_generation_time = timezone.now().isoformat()
        
        request.session['otp'] = otp
        request.session['otp_generation_time'] = otp_generation_time
        
        send_mail(
            'Resend OTP - Welcome to our site',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_MAIL,
            [user_data['email']],
            fail_silently=False,
        )
        messages.success(request,'A new OTP has been sent to your email')
    else:
        messages.error(request, 'No user data found. Please enter detail again')
    return redirect('verify_otp')

def login_page(request):
    if request.method =='POST':
        form = loginform(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user = authenticate(request, username=email,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,'successfully logged in')
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = loginform()
    return render(request,'userpart/user_panel/login_page.html',{'form':form})



def home(request):
    try:
        categories = Category.objects.filter(is_listed=True)[:4]
        products = Product.objects.filter(is_active=True)[:4]
        
        context ={
            'products' : products,
            'categories' : categories
        }

        if request.user.is_authenticated:
            context['user'] = request.user
            
        return render(request, 'userpart/user_panel/home_page.html', context)

    except ObjectDoesNotExist:
       
        context = {
            'products': [],
            'categories':[],
        }
        return render(request, 'userpart/user_panel/home_page.html', context)


def signout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')

























# def signup(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             request.session['user_data']=form.cleaned_data
#             otp = get_random_string(length=6,allowed_chars= '1234567890')
#             print(otp)
#             otp_generation_time=timezone.now().isoformat()
            
#             request.session['otp'] = otp
#             request.session['otp_generation_time'] = otp_generation_time
            
#             send_mail(
#                 'Welcome to our site',
#                 f'Your OTP is {otp}',
#                 settings.DEFAULT_FROM_MAIL,
#                 [form.cleaned_data['email']],
#                 fail_silently=False,
#             )
            
#             return redirect('verify_otp')  
#     else:
#         form = UserRegistrationForm()

#     return render(request, 'userpart/user_panel/signup_page.html', {'form': form})

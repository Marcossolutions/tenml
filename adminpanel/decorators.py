from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('adminpanel:admin_login') 
        if not request.user.is_staff and not request.user.is_superuser:
            return redirect('adminpanel:admin_login') 
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped_view)

from django.shortcuts import redirect
from functools import wraps

def superuser_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Check if the user is authenticated and is a superuser
        if request.user.is_authenticated and request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            # Redirect to login if the user is not a superuser
            return redirect('admin_panel:admin_login')  
    return wrap

from django.shortcuts import redirect
from django.urls import reverse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            # Example: Restrict /staff/ to Staff role
            if path.startswith('/staff/') and request.user.role != 'STAFF':
                return redirect('home')
            # Example: Restrict /admin-panel/ to Admin role
            if path.startswith('/admin-panel/') and request.user.role != 'ADMIN':
                 return redirect('home')
        
        response = self.get_response(request)
        return response

def role_required(allowed_roles):
    """
    Decorator for views that checks if user has the required role.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return redirect('home') # Or unauthorized page
        return _wrapped_view
    return decorator

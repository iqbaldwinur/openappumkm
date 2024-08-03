from django.http import HttpResponse
from django.shortcuts import redirect

def role_required(allowed_roles=None):
    allowed_roles = allowed_roles or []
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and (request.user.role in allowed_roles or request.user.is_superuser):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Unauthorized', status=401)
        return wrapper
    return decorator
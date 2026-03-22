from django.http import JsonResponse
from functools import wraps

def ajax_required(func):
    """Decorator to ensure request is AJAX"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Decorator to ensure user is staff"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Staff access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
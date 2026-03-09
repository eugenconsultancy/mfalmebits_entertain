from django.http import HttpResponseBadRequest
from functools import wraps

def ajax_required(view_func):
    """
    Decorator to ensure that the view is only accessed via AJAX.
    Returns a HttpResponseBadRequest (400) if the request is not AJAX.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseBadRequest('This view can only be accessed via AJAX.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
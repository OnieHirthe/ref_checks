from django.http import Http404
import functools

def group_required_404(group_list):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.groups.filter(name__in=group_list).exists():
                    return view_func(request, *args, **kwargs)
            raise Http404()
        return wrapper_func
    return decorator

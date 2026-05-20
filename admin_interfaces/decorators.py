from django.http import Http404

def group_required_404(group_list):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                print(request.user.groups.all())
                for group in request.user.groups.all():
                    if group.name in group_list:
                        return view_func(request, *args, **kwargs)
            raise Http404
        return wrapper_func
    return decorator

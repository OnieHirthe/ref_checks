from django.shortcuts import redirect
from django.http import Http404
from users.models import Report, PresentationFile, ExpertiseFile
from django.conf import settings

# add here something in repsonse header to open login shade
def	login_required_redirect(view_func):
    def wrapper_func(request, *args, **kwargs):
    
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            request.session['next_path'] = request.path
            return redirect("main_page_conference")

    return wrapper_func


# if file model instance is supposed to exist, checks that it does
def file_check_404(view_func):
    def wrapper_func(request, *args, **kwargs): 

        model = kwargs.get('model', None)
        file_id = kwargs.get('file_id', None)
        print(model, file_id)

        if file_id is not None:
            try:
                if model == 'presentation':
                    file_instance = PresentationFile.objects.get(id=file_id)
                elif model == 'expertise':
                    file_instance = ExpertiseFile.objects.get(id=file_id)
                    print("found instance")
                else:
                    raise Http404()
            except:
                raise Http404()
            else:
                kwargs['file_instance'] = file_instance

        return view_func(request, *args, **kwargs)

    return wrapper_func


def report_check_404(view_func):
    def wrapper_func(request, *args, **kwargs):
    
        report_id = kwargs.get('report_id', None)
        print("in rep dec", report_id)
        try:
            report_instance = Report.objects.get(id=report_id)
            print("found rep")
        except Exception as e:
            print(e)
            raise Http404()
        else:
            kwargs['report_instance'] = report_instance

        return view_func(request, *args, **kwargs)

    return wrapper_func


def check_stage(flag):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # no closure for admins
            if hasattr(request.user, 'is_admin') and request.user.is_admin():
                return view_func(request, *args, **kwargs)

            if settings.CONF_FLAGS[flag]:
                return view_func(request, *args, **kwargs)
            else:
                raise Http404()
        return wrapper_func
    return decorator




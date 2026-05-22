from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.urls import reverse
from django.views.decorators.cache import never_cache 
from users.forms import *
from users.decorators import *
from kmu.utils import year
from users.models import AuthLink
from users.emails import issue_verification, issue_code
from django.conf import settings

@never_cache
def register(request):
   
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserAuthRegistrationForm(request.POST)
        # so many things to check in validation
        if form.is_valid():
            # check if unconfirmed email exists
            potential_user = UserAuth.objects.filter(email=form.cleaned_data['email'])
            if potential_user.count() == 1:
                user = potential_user.first()
            else:
                user = UserAuth.objects.create_user(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            issue_verification(user, request)
            return render(request, "users/register_form.html", {"success" : True})
        else:
            return render(request, "users/register_form.html", {"register_form" : form })
    else:
        return render(request, "users/register_form.html", {"register_form" : UserAuthRegistrationForm()})

@never_cache
def confirm_registration(request, auth_link_id):
    
    if request.user.is_authenticated:
        return redirect("main_page_conference")

    
    auth_link = AuthLink.objects.filter(id=auth_link_id)

    if auth_link.count() != 1:
        raise Http404()
    else:
        user = UserAuth.objects.get(id=auth_link.first().user.id)
        user.is_confirmed = True
        user.save()
        auth_link.delete()
        return render(request, "tech/tech_auth_confirm.html")
    
    
@never_cache
def change_password_external(request):
    
    if request.method == 'POST':
        form = PasswordChangeExternalForm(request.POST)
        # check that user with the email exists
        if form.is_valid():
            # issue an email
            auth_id = issue_code(form.user)
            # redirect to code confirmation
            return redirect("change_password_code", auth_id=auth_id)
        else:
            return render(request, "users/password_change_external_form.html", {"pass_change_form" : form })
    else:
        return render(request, "users/password_change_external_form.html", {"pass_change_form" : PasswordChangeExternalForm() })

@never_cache
def change_password_code(request, auth_id):
    
    if request.method == 'POST':
        form = PasswordChangeCodeForm(request.POST, auth_id=auth_id)
        if form.is_valid():
            # log them in
            login(request, form.user)
            
            return redirect("change_password")
        else:
            return render(request, "users/password_change_code_form.html", {"pass_change_form" : form, "auth_id" : auth_id })
    else:
        return render(request, "users/password_change_code_form.html", {"pass_change_form" : PasswordChangeCodeForm(), "auth_id" : auth_id })


@never_cache
def change_password(request):

    if not request.user.is_authenticated:
        return render(request, "users/password_change_form.html", context={"failure" : True})

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            logout(request)
            return render(request, "users/password_change_form.html", context={"success" : True})
        else:
            return render(request, "users/password_change_form.html", {"pass_change_form" : form })
    else:
        return render(request, "users/password_change_form.html", {"pass_change_form" : PasswordChangeForm() })


@never_cache
def login_auth(request):
    
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserAuthLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            response = HttpResponse()
            response.headers['Hx-Redirect'] = reverse('profile')
            return response
        else:
            return render(request, "users/login_form.html", {"login_form" : form })
    else:
        return render(request, "users/login_form.html", {"login_form" : UserAuthLoginForm()})

@never_cache
@login_required_redirect
def logout_auth(request):
    logout(request)
    return redirect('main_page_conference')

@never_cache
@login_required_redirect
def profile(request):
    
    if hasattr(request.user,  "profile"):
        sees_online = request.user.unlisted() and request.user.profile.is_registered() and (request.user.profile.get_participation().online or request.user.is_admin())

        # for online section links
        if request.user.profile.any_reports_this_year():
            own_sections = Section.objects.filter(id__in=request.user.profile.reports.exclude(status="declined").distinct("section").values("section"))
            sections = Section.objects.exclude(id__in=own_sections)
        else:
            own_sections = []
            sections = Section.objects.all()
        context = { "own_sections" : own_sections, "sections" : sections, "sees_online" : sees_online }
    else:
        context = {}  
    return render(request, "users/profile_main.html", context)



@login_required_redirect
def profile_endpoint(request):

    citizenship = None

    if request.user.has_profile():
        profile_instance = request.user.profile 
        if profile_instance.citizenship is not None:
            if request.LANGUAGE_CODE == 'ru':
                citizenship = profile_instance.citizenship.title_ru
            else:
                citizenship = profile_instance.citizenship.title_en
    else:
        profile_instance = Profile(user=request.user)
    
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_instance)
        if form.is_valid():
            profile_instance = form.save()
            if 'email' in form.changed_data:
                request.user.email = form.cleaned_data['email']
                request.user.save()
            return render(request, "users/profile_form.html", {
                "profile_instance" : profile_instance})
        else:
            return render(request, "users/profile_form.html", {"profile_form" : form})

    else:
        if "form" in request.resolver_match.url_name or not profile_instance.all_required_filled():
            return render(request, "users/profile_form.html", {
                "profile_form" : ProfileForm(instance=profile_instance, initial={'email' : request.user.email, 'citizenship' : citizenship})
            })

        else:
            return render(request, "users/profile_form.html", {
            "profile_instance" : profile_instance })

@login_required_redirect
def citizenship_endpoint(request):
    query = request.GET.get('query', '')
    cform = CitizenshipForm(query=query, language=request.LANGUAGE_CODE, initial={"citizenship" : query})
    return render(request, "users/citizenship.html", context={"cform" : cform}) 


@check_stage("REGISTRATION")
@login_required_redirect
def participation_endpoint(request):

    if not request.user.has_profile() or not request.user.profile.all_required_filled():
        return render(request, "users/participation_form.html", context={"forbidden" : True})


    if request.user.profile.is_registered():
        participation_instance = request.user.profile.get_participation()
    else:
        participation_instance = Participation(profile=request.user.profile)

    if request.method == "POST":
        form = ParticipationForm(request.POST, instance=participation_instance)
        if form.is_valid():
            participation_instance = form.save()
            return render(request, "users/participation_form.html", {
                "participation_instance" : participation_instance })
        else:
            return render(request, "users/participation_form.html", {
                    "participation_form" : form })
    else:
        if "form" in request.resolver_match.url_name or not request.user.profile.is_registered():
            return render(request, "users/participation_form.html", {
                "participation_form" : ParticipationForm(instance=participation_instance),   
            })
        else:
            return render(request, "users/participation_form.html", {
            "participation_instance" : participation_instance })

@check_stage("REPORT_SUBMISSION")
@login_required_redirect
def author_endpoint(request, advisor, author_id=None):
    if advisor:
        template = "users/advisor_form.html"
    else:
        template = "users/author_form.html"

    author_instance = Author.objects.safe_get(id=author_id)
    if author_id is not None and author_instance is None:
        raise Http404()
    
    if request.method == "POST":
        form  = AuthorForm(request.POST, instance=author_instance)
        if form.is_valid():
            form.instance.advisor = advisor
            author_instance = form.save()
            return render(request, template, context={"author_instance" : author_instance})
        else:
            return render(request, template, context={"author_form" : form})

    else:
        if "form" in request.resolver_match.url_name:
            return render(request, template, context={"author_form" : AuthorForm(instance=author_instance)})
        else:
            if author_instance is not None:
                return render(request, template, context={"author_instance" : author_instance}) 
            else:
                raise Http404()


@login_required_redirect
def reports_endpoint(request, report_id=None):
    
    if not request.user.has_profile() or not request.user.profile.all_required_filled() or not request.user.profile.is_registered():
        raise Http404()

    reports = Report.objects.filter(profile=request.user.profile, year=year()).order_by('created')
    
    report_instance = Report.objects.safe_get(id=report_id)
    
    if report_id is not None:
        if report_instance is None:
            raise Http404()
    else:
        report_instance = Report(profile=request.user.profile, year=year())


    if request.method == "POST":

        if not settings.CONF_FLAGS["REPORT_SUBMISSION"]:
            raise Http404()

        form = ReportForm(request.POST, instance=report_instance)
        if form.is_valid():
            
            report_instance = form.save()
            report_instance.set_authors(form.cleaned_data['authors_field'])
            return render(request, "users/reports.html", context={"reports" : reports})
        else:
            return render(request, "users/reports.html", context={"report_form" : form})
    else:
        if "form" in request.resolver_match.url_name:
            if not settings.CONF_FLAGS["REPORT_SUBMISSION"]:
                raise Http404()

            return render(request, "users/reports.html", context={"report_form" : ReportForm(instance=report_instance), "reports" : reports})
        else:
            return render(request, "users/reports.html", context={"reports" : reports})


@check_stage("REPORT_SUBMISSION")
@login_required_redirect
def delete_report(request, report_id):

    report_instance = Report.objects.safe_get(id=report_id)
    if report_instance is None:
        raise Http404()
    
    report_instance.delete()

    return redirect("reports_endpoint")

@check_stage("REGISTRATION")
@login_required_redirect
def delete_participation(request):
    
    if not request.user.profile.is_registered():
        raise Http404()

    participation_instance = request.user.profile.get_participation()

    participation_instance.delete()

    return redirect("participation_endpoint")

@check_stage("REPORT_SUBMISSION")
@login_required_redirect
def delete_author(request, author_id):

    author_instance = Author.objects.safe_get(id=author_id)
    if author_instance is None:
        raise Http404()
    
    author_instance.delete()

    return HttpResponse("")

def report_public_page(request, report_id):
    
    report_instance = Report.objects.safe_get(id=report_id)
    
    if report_instance is None:
        raise Http404()

    if report_instance.status == 'declined':

        if not request.user.is_authenticated:
            raise Http404()
        

    return render(request, "users/public_report_page.html", context={ 'report' : report_instance })




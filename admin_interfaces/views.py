from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from kmu.utils import year as current_year
from users.models import Profile, Report, Subsection, Section
from users.decorators import report_check_404
from admin_interfaces.models import BlackListedEntry
from admin_interfaces.forms import * 
from admin_interfaces.decorators import group_required_404
from django.db.models import Count, F
import datetime as dt
import csv


#single procedure for table and csv
def filter_participants(request, year):
    
    citizenship = request.GET.get('citizenship', None)
    online = request.GET.get('online', None)
    reports = request.GET.get('reports', None)

    profiles_qs = Profile.objects\
        .filter(participations__year=year)\
        .prefetch_related('user', 'citizenship', 'participations')\
        .annotate(\
            bl_class=F('user__in_bl__level'),\
            rep_count=Count('reports', filter=Q(reports__year=year)),\
            online=F('participations__online'),\
            date_reg=F('participations__created'))
    
    if citizenship is not None:
        if citizenship == "russian":
            profiles_qs = profiles_qs.filter(citizenship__code="RU")
        else:
            profiles_qs = profiles_qs.exclude(citizenship__code="RU")

    if online is not None:
        online_bool = True if online == "True" else False
        profiles_qs = profiles_qs.filter(participations__online=online_bool)

    if reports is not None:
        if reports == "no":
            profiles_qs = profiles_qs.filter(rep_count=0)
        else:
            profiles_qs = profiles_qs.filter(rep_count__gt=0)

    profiles = profiles_qs.order_by("-date_reg")
    
    return profiles, {"citizenship" : citizenship, "online" : online, "reports" : reports}


@group_required_404(group_list=["org", "admin"])
def participant_list(request, year=current_year()):

    if year not in settings.CONF_YEARS:
        year = current_year()

    profiles, filter_dict = filter_participants(request, year)

    return render(request, "admin_interfaces/participant_list.html", context={
        "profiles" : profiles, 
        "filter_form" : FilterForm(initial=filter_dict), 
        "current_year" : year })



@group_required_404(group_list=["org", "admin"])
def participant_csv(request, year=current_year()):
    
    profiles, filter_dict = filter_participants(request, year)
    
    filter_str = "_".join([ f"{key}_{value}".lower() if value is not None else "" for key, value in filter_dict.items() ])
    timestamp = str(dt.datetime.now()).replace(' ', '_').replace(':', '_')
    
    filename = f"kmu_participants_{filter_str}_{timestamp}.csv"
    
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

    #fieldnames = ["last_name_ru", "first_name_ru", "middle_name_ru", "organization_ru", "org_short_ru", "position_ru",
    #"last_name_en", "first_name_en", "organization_en", "org_short_en", "position_en", "online", "reports",
    #"citizenship_code", "citizenship_ru", "email", "phone", "registered_website", "registered_conference" ]

    #fieldnames = ["lang", "name_ru", "name_en", "org_short_ru", "org_short_en", "org_ru", "org_en"]
    
    fieldnames = ["last_name", "first_name", "middle_name", "org", "blacklisted"]

    writer = csv.DictWriter(response, fieldnames=fieldnames, delimiter="*")
    writer.writeheader()
    for inst in profiles:
        if inst.reports.count() > 0:
            lang = inst.reports.first().lang
        else:
            lang = 'ru' if inst.last_name_ru is not None else 'en'
    
        first_name = getattr(inst, f"first_name_{lang}", lambda: "")
        last_name = getattr(inst, f"last_name_{lang}", lambda: "")
        middle_name = inst.middle_name_ru if lang == 'ru' else ''
        if getattr(inst, f"org_short_{lang}") is None or getattr(inst, f"org_short_{lang}") == "":
            org = getattr(inst, f"org_{lang}")
        else:
            org = getattr(inst, f"org_short_{lang}") 
        
        if inst.user.graylisted():
            listed = "!"
        elif inst.user.blacklisted():
            listed = "!!!"
        else:
            listed = ""

        writer.writerow({
            "last_name" : last_name,
            "first_name" : first_name,
            "middle_name" : middle_name,
            "org" : org,
            "blacklisted": listed,
            #"lang" : inst.reports.first().lang if inst.reports.count() > 0 else "",
            #"name_ru" : inst.full_rus_name(),
            #"name_en" : inst.full_en_name(),
            #"org_short_ru" : inst.org_short_ru,
            #"org_short_en" : inst.org_short_en,
            #"org_ru" : inst.org_ru,
            #"org_en" : inst.org_en
            #"last_name_ru" : inst.last_name_ru,
            #"first_name_ru" : inst.first_name_ru,
            #"middle_name_ru" : inst.middle_name_ru,
            #"organization_ru" : inst.org_ru,
            #"org_short_ru" : inst.org_short_ru,
            #"position_ru" : inst.position_ru,
            #"last_name_en" : inst.last_name_en,
            #"first_name_en" : inst.first_name_en,
            #"organization_en" : inst.org_en,
            #"org_short_en" : inst.org_short_en,
            #"position_en" : inst.position_en,
            #"online" :  inst.online,
            #"reports" : inst.rep_count,
            #"citizenship_code" : "" if inst.citizenship is None else inst.citizenship.code,
            #"citizenship_ru" : "" if inst.citizenship is None else inst.citizenship.title_ru,
            #"email" : inst.user.email,
            #"phone" : inst.phone,
            #"registered_website" : inst.user.created,
            #"registered_conference" : inst.date_reg
        })

    return response


@group_required_404(group_list=["admin"])
def everything_json(request, year=current_year()):
    profiles, filter_dict = filter_participants(request, year)
    
    filter_str = "_".join([ f"{key}_{value}".lower() if value is not None else "" for key, value in filter_dict.items() ])
    timestamp = str(dt.datetime.now()).replace(' ', '_').replace(':', '_')
    
    content_dicts = []
    
    for profile in profiles:
        content_dict = {}
        profile_data = {
            "email" : profile.user.email,
            "last_name_ru" : profile.last_name_ru,
            "first_name_ru" : profile.first_name_ru,
            "middle_name_ru" : profile.middle_name_ru,
            "last_name_en" : profile.last_name_en,
            "first_name_en" : profile.first_name_en,
            "organization_ru" : profile.org_ru,
            "organization_en" : profile.org_en,
            "org_short_ru" : profile.org_short_ru,
            "org_short_en" : profile.org_short_en,
            "position_ru" : profile.position_ru,
            "position_en" : profile.position_en,
            "citizenship" : "" if profile.citizenship is None else profile.citizenship.title_ru,

            "participation_type" : "online" if profile.get_participation_year(year).online else "offline",
        }
        
        reports_data =[]
        for report in profile.reports.all():
            
            has_advisor = report.has_advisor and hasattr(report, "advisor") and report.advisor is not None
            
            report_data = {
                "language" : report.lang, 
                "title" : report.title,
                "abstract" : report.abstract, 
                "publication_link" : report.pub_link, 
                "advisor" : None if not has_advisor else {
                        "last_name" : report.advisor.last_name,
                        "first_name" : report.advisor.first_name,
                        "middle_name" : report.advisor.middle_name,
                        "email" : report.advisor.email,
                        "organization" : report.advisor.org,
                    }, 
                "plenary" : report.plenary, 
                "section" : report.section.name_ru, 
            }
            authors = []
            for author in report.authors_only():
                author_data = {
                    "last_name" : author.last_name,
                    "first_name" : author.first_name,
                    "middle_name" : author.middle_name,
                    "email" : author.email,
                    "organization" : author.org,
                }
                authors.append(author_data)
            report_data["authors"] = authors
            reports_data.append(report_data)

        content_dict["profile"] = profile_data
        content_dict["reports"] = reports_data
        content_dicts.append(content_dict)

    
    return JsonResponse({"user_data" : content_dicts})


#single procedure for table and csv
def filter_reports(request, year):

    status = request.GET.get('status', None)
    section_id = request.GET.get('section_id', None)
    citizenship = request.GET.get('citizenship', None)
    online = request.GET.get('online', None)

    reports_qs = Report.objects.filter(year=year, profile__participations__isnull=False).distinct().prefetch_related('profile', 'profile__user', 'profile__citizenship', 'profile__participations')
   
    if status is not None:
        reports_qs = reports_qs.filter(status=status)

    if section_id is not None:
        reports_qs = reports_qs.filter(section__id=section_id)

    if citizenship is not None:
        if citizenship == "russian":
            reports_qs = reports_qs.filter(profile__citizenship__code="RU")
        else:
            reports_qs = reports_qs.exclude(profile__citizenship__code="RU")
    
    if online is not None: 
        online_bool = True if online == "True" else False
        reports_qs = reports_qs.filter(profile__participations__online=online_bool)


    reports = reports_qs.annotate(online=F('profile__participations__online'), bl_class=F('profile__user__in_bl__level')).order_by("-created")
    
    #filter form is not to be validated
    return reports, {"status" : status, "section_id" : section_id, "citizenship" : citizenship, "online" : online}



@group_required_404(group_list=["org", "admin"])
def report_list(request, year=current_year()):
    
    if year not in settings.CONF_YEARS:
        year = current_year()

    reports, filter_dict = filter_reports(request, year)

    return render(request, "admin_interfaces/report_list.html", context={
        "reports" : reports, 
        "filter_form" : FilterForm(initial=filter_dict),
        "current_year" : year,
        })

@group_required_404(group_list=["org", "admin"])
def report_csv(request, year=current_year()):
    
    reports, filter_dict = filter_reports(request, year)
    
    filter_str = "_".join([ f"{key}_{value}".lower() if value is not None else "" for key, value in filter_dict.items() ])
    timestamp = str(dt.datetime.now()).replace(' ', '_').replace(':', '_')
    
    filename = f"kmu_reports_{filter_str}_{timestamp}.csv"
    
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

    fieldnames = ["status", "title", "online", "language", "participant_ru", "participant_en", "participant_email",
    "citizenship_code", "citizenship_ru", "org_ru", "org_en", "section", "subsection", "created",
    "expertise_attached", "presentation_attached"]
    
    fieldnames_short = ["status", "title", "full_name", "authors", "page_link", "org_short", "org", "section", "subsection"]

    writer = csv.DictWriter(response, fieldnames=fieldnames_short, delimiter="*")
    writer.writeheader()
    for inst in reports:
        writer.writerow({
            "status" : inst.status,
            "title" : inst.title,
            "full_name" : inst.profile.full_rus_name() if inst.lang == 'ru' else inst.profile.full_en_name(),
            "authors" : inst.full_authors(),
            #"online" : inst.online,
            #"language" : inst.lang,
            #"participant_ru" : inst.profile.full_rus_name(),
            #"participant_en" : inst.profile.full_en_name(),
            #"participant_email" : inst.profile.user.email,
            #"citizenship_code" : inst.profile.citizenship.code if inst.profile.citizenship is not None else "",
            #"citizenship_ru" : inst.profile.citizenship.title_ru if inst.profile.citizenship is not None else "",
            "org" : f"{inst.profile.org_ru} ({inst.profile.org_en})",
            "org_short" : f"{inst.profile.org_short_ru} ({inst.profile.org_short_en})",
            "page_link": request.build_absolute_uri(reverse('report_public_page', kwargs={ 'report_id' : inst.id })),
            "section" : inst.section.name_ru,
            "subsection" : inst.subsection.name_ru if inst.subsection else "",
            #"created" : inst.created,
            #"expertise_attached" : inst.has_expertise(),
            #"presentation_attached" : inst.has_presentation()
        })

    return response
    



@group_required_404(group_list=["admin"])
def subsection_list(request):
    sections = Section.objects.order_by("name_ru")
    return render(request, "admin_interfaces/subsection_list.html", context={"sections" : sections})

@group_required_404(group_list=["admin"])
def broadcast_section_list(request):
    sections = Section.objects.order_by("name_ru")
    return render(request, "admin_interfaces/broadcast_section_list.html", context={"sections" : sections})

@group_required_404(group_list=["admin"])
def profile_view(request, profile_id):

    try:
        profile_instance = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        raise Http404()

    if request.method == 'GET':
        return render(request, "admin_interfaces/profile_view.html", context={"profile_instance" : profile_instance})


@group_required_404(group_list=["admin"])
def report_view(request, report_id):

    try:
        report_instance = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        raise Http404()

    if request.method == 'GET':
        return render(request, "admin_interfaces/report_view.html", context={"report" : report_instance })


@group_required_404(group_list=["admin"])
@report_check_404
def report_chat(request, report_id, comment_id=None, **kwargs):
    report_instance = kwargs.get('report_instance')
   
    if comment_id is not None:
        try:
            comment_instance = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise Http404()
    else:
        comment_instance = None

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment_instance, report=report_instance, profile=request.user.profile)
        if form.is_valid():
            comment_instance = form.save()
            return render(request, "admin_interfaces/chat.html", context={"report" : report_instance, "comment_instance" : comment_instance})
        else:
            return render(request, "admin_interfaces/chat.html", context={ "report"  : report_instance, "form" : form, "comment_instance" : comment_instance })
    else:
        if "form" in request.resolver_match.url_name:
            return render(request, "admin_interfaces/chat.html", context={ "report"  : report_instance, "form" : CommentForm(instance=comment_instance, report=report_instance, profile=request.user.profile), "comment_instance" : comment_instance })
        else:
            return render(request, "admin_interfaces/chat.html", context={"report" : report_instance, "comment_instance" : comment_instance})


@group_required_404(group_list=["admin"])
def del_chat_comment(request, comment_id):
    try:
        comment_instance = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        raise Http404()
    
    report = comment_instance.report
    
    if request.user.profile == comment_instance.profile:
        comment_instance.delete()
    
    return redirect("report_chat", report_id=report.id)



@group_required_404(group_list=["admin"])
def black_list(request):
    return render(request, "admin_interfaces/black_list.html", {"black_list" : BlackListedEntry.objects.order_by("-created")})


@group_required_404(group_list=["admin"])
def black_listed_user_endpoint(request):
    query = request.GET.get('query', '')
    uform = BlackListedUserForm(query=query, initial={"user" : query })
    return render(request, "admin_interfaces/bl_user_form.html", context={"uform" : uform})


@group_required_404(group_list=["admin"])
def black_list_entry(request, bl_id=None):
    if bl_id is not None:
        try:
            black_listed_instance = BlackListedEntry.objects.get(id=bl_id)
        except BlackListedEntry.DoesNotExist:
            raise Http404()
    else:
        black_listed_instance = None
    if request.method == "POST":
        form = BlackListedForm(request.POST, instance=black_listed_instance)
        if form.is_valid():
            form.instance.profile = request.user.profile
            form.save()
            response = HttpResponse()
            response.headers['Hx-Redirect'] = reverse('black_list')
            return response
        else:
            return render(request, "admin_interfaces/black_listed_form.html", {"form" : form })

    else:
        if black_listed_instance:
            return render(request, "admin_interfaces/black_listed_form.html", {"form" : BlackListedForm(instance=black_listed_instance), "instance" : black_listed_instance })
        else:
            return render(request, "admin_interfaces/black_listed_form.html", {"form" : BlackListedForm()})
    

@group_required_404(group_list=["admin"])
def bl_entry_delete(request, bl_id):
    try:
        black_listed_instance = BlackListedEntry.objects.get(id=bl_id)
    except BlackListedEntry.DoesNotExist:
        raise Http404()

    black_listed_instance.delete()
    
    return redirect('black_list')




from django.shortcuts import render, redirect 
from django.http import Http404
from users.models import Profile, Report, Subsection, Section
from users.decorators import report_check_404
from admin_interfaces.models import Comment
from admin_interfaces.forms import *
from admin_interfaces.decorators import group_required_404

FIELDFORM = {
    "title" : ReportTitleForm,
    "abstract" : ReportAbstractForm,
    "plenary" : ReportPlenaryForm,
    "lang" : ReportLanguageForm,
    "pub_link" : ReportPublinkForm,
}


@group_required_404(group_list=["admin"])
@report_check_404
def report_attach_section(request, report_id, **kwargs):
    report_instance = kwargs.get('report_instance')

    if request.method == "POST":
        form = SectionAttachForm(request.POST)
        if form.is_valid():
            prev_section = report_instance.section
            new_section = Section.objects.get(id=form.cleaned_data['section_id'])
            if prev_section != new_section:
                report_instance.section = new_section
                report_instance.subsection = None
                report_instance.save()
                comment = Comment(auto=True, report=report_instance, profile=request.user.profile, content=f"changed section from '{prev_section.name_ru}' to '{new_section.name_ru}'")
                comment.save()
                return render(request, "admin_interfaces/section_attach_form.html", context={ 'report' : report_instance, "changed" : True })
            else:
                return render(request, "admin_interfaces/section_attach_form.html", context={ 'report' : report_instance, "changed" : False })

    if "form" in request.resolver_match.url_name:
        return render(request, "admin_interfaces/section_attach_form.html", context={ "form" : SectionAttachForm(initial={'section_id' : report_instance.section.id }), 'report' : report_instance })
    else:
        return render(request, "admin_interfaces/section_attach_form.html", context={ 'report' : report_instance })



@group_required_404(group_list=["admin"])
@report_check_404
def report_attach_subsection(request, report_id, **kwargs):
    report_instance = kwargs.get('report_instance')

    if request.method == "POST":
        form = SubsectionAttachForm(request.POST, section=report_instance.section)
        if form.is_valid():
            subsection = Subsection.objects.get(id=form.cleaned_data['subsection_id'])
            report_instance.subsection = subsection
            report_instance.save()
            return render(request, "admin_interfaces/subsection_attach_form.html", context={ 'report' : report_instance })
    
    if "form" in request.resolver_match.url_name: 
        if report_instance.subsection:
            return render(request, "admin_interfaces/subsection_attach_form.html", context={"form" : SubsectionAttachForm(section=report_instance.section, initial={'subsection_id' : report_instance.subsection.id } ), 'report' : report_instance })
        else:
            return render(request, "admin_interfaces/subsection_attach_form.html", context={"form" : SubsectionAttachForm(section=report_instance.section ), 'report' : report_instance })
    else:
        return render(request, "admin_interfaces/subsection_attach_form.html", context={'report' : report_instance})


@group_required_404(group_list=["admin"])
@report_check_404
def admin_report_field(request, report_id, **kwargs):
   
    report_instance = kwargs.get('report_instance')
    field = kwargs.get('field')
    Form = FIELDFORM[field]
    if field == "title":
        template = "admin_interfaces/admin_report_title_form.html"
    else:
        template = "admin_interfaces/admin_report_field_form.html"

    if request.method == "POST":
        form = Form(request.POST, instance=report_instance)
        if form.is_valid():
            changed = False
            if form.has_changed():
                changed = True
                report_instance = form.save()
                comment = Comment(auto=True, report=report_instance, profile=request.user.profile, content=f"changed field '{field}' value")
                comment.save()
            return render(request, template, { 'value' : getattr(report_instance, field), 'report' : report_instance, 'changed' : changed })

    context = {
        'field' : field,
        'report' : report_instance,
        'url_name' : f"admin_report_{ field }", 
    }

    if "form" in request.resolver_match.url_name:
        context['form'] = Form(instance=report_instance)
    else:
        context['value'] = getattr(report_instance, field)

    return render(request, template, context)

@group_required_404(group_list=["admin"])
@report_check_404
def admin_report_has_advisor(request, report_id, **kwargs):
    report_instance = kwargs.get('report_instance')

    changed = False
    if request.method == 'POST':
        form = ReportHasAdvisorForm(request.POST, instance=report_instance)
        if form.is_valid():
            if form.has_changed():
                changed = True
                report_instance = form.save()
                comment = Comment(auto=True, report=report_instance, profile=request.user.profile, content=f"changed field 'has_advisor' value")
                comment.save()

    else:
        form = ReportHasAdvisorForm(instance=report_instance)

    report_instance = kwargs.get('report_instance')
    return render(request, "admin_interfaces/admin_report_has_advisor_form.html", {
        'report' : report_instance,
        'form' : form,
        'changed' : changed
        
    })


@group_required_404(group_list=["admin"])
@report_check_404
def admin_report_attach_authors(request, report_id, **kwargs):
    report_instance = kwargs.get('report_instance')

    changed = False
    if request.method == 'POST':
        form = ReportAuthorsForm(request.POST, instance=report_instance)
        if form.is_valid():
            if form.has_changed():
                changed = True
                report_instance.set_authors(form.cleaned_data['authors_field'])
                comment = Comment(auto=True, report=report_instance, profile=request.user.profile, content=f"changed field 'authors' value")
                comment.save()

    return render(request, "admin_interfaces/admin_report_attach_authors.html", {
        'report' : report_instance, 
        'form' : ReportAuthorsForm(instance=report_instance),
        'changed' : changed
    })

@group_required_404(group_list=["admin"])
def handle_subsection(request, section_id, subsection_id=None):
    try:
        section_instance = Section.objects.get(id=section_id)
    except:
        raise Http404()

    if subsection_id is not None:
        try:
            subsection_instance = Subsection.objects.get(id=subsection_id)
        except:
            raise Http404()
    else:
        subsection_instance = None

    if request.method == "POST":
        form = SubsectionForm(request.POST, instance=subsection_instance, section=section_instance)
        if form.is_valid():
            subsection_instance = form.save()
            return render(request, "admin_interfaces/subsection_form.html", context={ "instance" : subsection_instance, "section" : section_instance })
        else:
            return render(request, "admin_interfaces/subsection_form.html", context={ "form" : form, "section" : section_instance })

    else:
        if "form" in request.resolver_match.url_name:
            return render(request, "admin_interfaces/subsection_form.html", context={ "form" : SubsectionForm(instance=subsection_instance, section=section_instance), "instance" : subsection_instance, "section" : section_instance })
        else:
            return render(request, "admin_interfaces/subsection_form.html", context={"instance" : subsection_instance, "section" : section_instance })


@group_required_404(group_list=["admin"])
def delete_subsection(request, subsection_id):

    try:
        subsection_instance = Subsection.objects.get(id=subsection_id)
    except Exception as e:
        raise Http404()

    subsection_instance.delete()
    return HttpResponse(status=200)



@group_required_404(group_list=["admin"])
def handle_section_broadcast_link(request, section_id):
    try:
        section_instance = Section.objects.get(id=section_id)
    except:
        raise Http404()


    if request.method == "POST":
        form = BroadcastSectionForm(request.POST, instance=section_instance)
        if form.is_valid():
            section_instance = form.save()
    else:
        form = BroadcastSectionForm(instance=section_instance)
    
    return render(request, "admin_interfaces/broadcast_link_form.html", context={"form" : form, "section" : section_instance })


@group_required_404(group_list=["admin"])
@report_check_404
def set_report_status(request, report_id, status=None, **kwargs):
    report_instance = kwargs.get('report_instance')

    if status is None:
        report_instance.status = 'in review'
    elif status == "accepted":
        report_instance.status = 'accepted'
    elif status == "declined":
        report_instance.status = 'declined'
    else:
        raise Http404()

    report_instance.save()
    comment = Comment(auto=True, report=report_instance, profile=request.user.profile, content=f"changed status to {report_instance.status.upper()}")
    comment.save()
    return redirect("admin_report", report_id=report_instance.id)






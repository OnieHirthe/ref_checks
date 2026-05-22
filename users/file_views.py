from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from users.forms import ReportFileForm
from users.decorators import *



def single_file_upload(single_file, report_instance, model):
    if model == 'presentation':
        repfile = PresentationFile(report=report_instance)
    if model == 'expertise':
        repfile = ExpertiseFile(report=report_instance)

    actual_name = single_file.name
    ending = actual_name.split(".")[-1]
    single_file.name = f"{repfile.id}.{ending}" if ending else f"{repfile.id}"
    repfile.filename = actual_name
    repfile.file_obj = single_file
    repfile.save()

    return repfile

@login_required_redirect
@report_check_404
@file_check_404
def handle_file(request, report_id, model, file_id=None, **kwargs):
    file_instance = kwargs.get("file_instance", None)
    report_instance = kwargs.get("report_instance", None)

    if request.method == "POST":
        file_form = ReportFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            file_instance = single_file_upload(file_form.cleaned_data["single_file"], report_instance, model)
            return render(request, "users/single_file.html", context={"file_instance" : file_instance, "model" : model, "report" : report_instance})
        else:
            return render(request, "users/single_file.html", context={"file_form" : file_form, "model" : model, "report" : report_instance})

    if request.method == "GET":
        if file_instance is not None:
            return render(request, "users/single_file.html", context={"file_instance" : file_instance, "report" : report_instance, "model" : model})
        else:
            return render(request, "users/single_file.html", context={"file_form" : ReportFileForm(), "model" : model, "report": report_instance })
    

@login_required_redirect
@file_check_404
def delete_file(request, model, file_id, **kwargs):
    file_instance = kwargs.get("file_instance", None)

    report_id = file_instance.report.id
    print("in file del", report_id)
    file_instance = kwargs.get("file_instance")
    file_instance.delete_file()
    file_instance.delete()

    print("in file del", report_id)
    
    return redirect("handle_file", report_id=report_id, model=model)

@login_required_redirect
@file_check_404
def display_file(request, model, file_id, **kwargs):
    
    file_instance = kwargs.get("file_instance")
    return FileResponse(file_instance.file_obj, filename=file_instance.filename)

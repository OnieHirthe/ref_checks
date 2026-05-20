from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
import os

from landing.emails import send_email, send_sub_notification, send_unsub_notification
from landing.models import *
from landing.forms import ContactForm


def standby(request):
    return render(request, 'standby.html')

def test_page(request):
    return render(request, 'landing/test_page.html', context={'form' : ContactForm()})

def main_page(request):
    return render(request, 'landing/main_page.html', context={'form' : ContactForm()})

def contact_endpoint(request):
    print("in contact view")
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # create instance if it does not exist
            subscriber = Subscriber.objects.get_or_none(email=form.cleaned_data['email'])
            if subscriber is None:
                subscriber = form.save()
                send_email(subscriber)
            # send_email
            send_sub_notification(form.cleaned_data['email'], form.cleaned_data['comment'])
            success = True
        else:
            success = False
            for item in form.errors.keys():
                form.fields[item].required = False
                form.fields[item].widget.attrs['class'] = "red-border"
        return render(request, 'landing/form.html', context={'form' : form, 'success' : success})

    form = ContactForm()
    return render(request, 'landing', context={'form' : form})


def unsubscribe(request, sub_id):
    sub = Subscriber.objects.get_or_none(id=sub_id)
    if sub is not None:
        send_unsub_notification(sub.email)
        sub.delete()
    
    return render(request, 'landing/technical.html') 


def get_agreement(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "politika-pers-dannykh.pdf")
    return FileResponse(open(file_name, "rb"))


def get_brochure(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "YSC2026.pdf")
    return FileResponse(open(file_name, "rb"))




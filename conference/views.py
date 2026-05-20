from django.shortcuts import render
from django.utils.translation import gettext as _
from kmu.utils import today, year
import datetime as dt
from users.decorators import check_stage


# Create your views here.

def main_page(request):
    return render(request, "conference/main.html", context={'page_title' : _("главная")})
    
def about_conference(request):
    return render(request, "conference/full_about_conference.html", context={'page_title' : _("о конференции")})

def for_participants(request):
    return render(request, "conference/full_for_participants.html", context={'page_title' : _("участникам")})

@check_stage("PROGRAM_PUBLIC")
def timetable(request, url_day=None):
    
    if url_day is None:
        
        days = [22, 23, 24]
        dates = [ dt.date(day=day, month=4, year=year()) for day in days ]
        
        if today() in dates:
            day = today().day
        else:
            day = 22
            
    else:
        day = url_day    
    
    return render(request, "conference/timetable.html", context={'page_title' : _("расписание 2026"), 'day' : day})


def get_404(request, exception):
    return render(request, "404.html", status=404)


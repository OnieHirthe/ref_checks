from django.http import FileResponse
import os
from django.conf import settings



def get_agreement_ru(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "KMU_personal_data_consent.pdf")
    return FileResponse(open(file_name, "rb"))

def get_agreement_en(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "YSC_personal_data_consent.pdf")
    return FileResponse(open(file_name, "rb"))

def get_brochure(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "YSC2026.pdf")
    return FileResponse(open(file_name, "rb"))


def get_proccedings_example_en(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "YSC_proceedings_example.docx")
    return FileResponse(open(file_name, "rb"))


def get_proccedings_guide_en(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "YSC_proceedings_guidelines.pdf")
    return FileResponse(open(file_name, "rb"))

def get_proccedings_example_ru(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "KMU_proceedings_example.docx")
    return FileResponse(open(file_name, "rb"))

def get_proccedings_guide_ru(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "KMU_proceedings_guidelines.pdf")
    return FileResponse(open(file_name, "rb"))


def get_timetable(request, lang='en', day=None, exact=True):
    path = settings.MEDIA_ROOT
 
    t_type = "full" if exact else "basic" 
    lang = '_eng' if lang == 'en' else ''

    if day is None or day not in range(22, 25):
        day = 1
        file_name = os.path.join(path, f"kmu_program/program26_{ t_type }{lang}.pdf")
    else:
        day = day - 21
        file_name = os.path.join(path, f"kmu_program/program26_{ t_type }{lang}_day{day}.pdf")
    
    return FileResponse(open(file_name, "rb"))

def get_zoom_room_instructions(request):
    path = settings.MEDIA_ROOT
    file_name = os.path.join(path, "zoom_rooms_instructions.pdf")
    return FileResponse(open(file_name, "rb"))




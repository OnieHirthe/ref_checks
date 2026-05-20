from django.urls import path
from conference import views
from conference import doc_views


urlpatterns = [
    path('', views.main_page, name="main_page_conference"),
    path('about_conference/', views.about_conference, name="about_conference"),
    path('for_participants/', views.for_participants, name="for_participants"),

    path('timetable/', views.timetable, name="timetable"),
    path('timetable/22/', views.timetable, {'url_day' : 22}, name="timetable_22"),
    path('timetable/23/', views.timetable, {'url_day' : 23}, name="timetable_23"),
    path('timetable/24/', views.timetable, {'url_day' : 24}, name="timetable_24"),

    path('data_agreement_ru/', doc_views.get_agreement_ru, name="get_agreement_ru"),
    path('data_agreement_en/', doc_views.get_agreement_en, name="get_agreement_en"),
    path('get_brochure/', doc_views.get_brochure, name="get_brochure"),
    
    path('get_proccedings_example_en/', doc_views.get_proccedings_example_en, name="get_example_en"),
    path('get_proccedings_guide_en/', doc_views.get_proccedings_guide_en, name="get_guide_en"),
    path('get_proccedings_example_ru/', doc_views.get_proccedings_example_ru, name="get_example_ru"),
    path('get_proccedings_guide_ru/', doc_views.get_proccedings_guide_ru, name="get_guide_ru"),

    path('get_timetable/basic/<str:lang>/<int:day>/', doc_views.get_timetable, {'exact' : False},  name="get_timetable_basic"),
    path('get_timetable/basic/<str:lang>/', doc_views.get_timetable, {'exact' : False},  name="get_timetable_basic"),
    path('get_timetable/full/<str:lang>/<int:day>/', doc_views.get_timetable, {'exact' : True},  name="get_timetable_full"),
    path('get_timetable/full/<str:lang>/', doc_views.get_timetable, {'exact' : True},  name="get_timetable_full"),
    
    path('get_to_zoom_room/', doc_views.get_zoom_room_instructions, name="get_to_zoom_room"),
]

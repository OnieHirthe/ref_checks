from django.urls import path
from landing import views

urlpatterns = [
    path('', views.standby),
    path('get_brochure/', views.get_brochure, name="get_brochure"),
]

from django.urls import path
from landing import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    #path('test/', views.test_page, name="test_page"),
    path('contact/', views.contact_endpoint, name="contact"),
    path('unsubscribe/<uuid:sub_id>/', views.unsubscribe, name="unsubscribe"),
    path('data_agreement/', views.get_agreement, name="get_agreement"),
    path('get_brochure/', views.get_brochure, name="get_brochure"),
]

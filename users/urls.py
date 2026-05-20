from django.urls import path
from users import views
from users import file_views


urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login_auth, name="login"),
    path('logout/', views.logout_auth, name="logout"),
    path('pass_reset/', views.change_password_external, name="reset_password"),
    path('pass_code/<uuid:auth_id>/', views.change_password_code, name="change_password_code"),
    path('pass_change/', views.change_password, name="change_password"),
   
    path('confirm_registration/<uuid:auth_link_id>/', views.confirm_registration, name="confirm_registration"),

    path('profile/', views.profile, name="profile"),
    
    path('profile_endpoint/', views.profile_endpoint, name="profile_endpoint"),
    path('profile_endpoint/get_form/', views.profile_endpoint, name="profile_endpoint_form"),
    path('profile/citizenship/', views.citizenship_endpoint, name="citizenship_endpoint"),

    path('participation_endpoint/', views.participation_endpoint, name="participation_endpoint"),
    path('participation_endpoint/get_form/', views.participation_endpoint, name="participation_endpoint_form"),
    path('delete_participation/', views.delete_participation, name="delete_participation"),

    path('reports_endpoint/', views.reports_endpoint, name="reports_endpoint"),
    path('reports_endpoint/<uuid:report_id>/', views.reports_endpoint, name="reports_endpoint"),
    path('reports_endpoint/get_form/', views.reports_endpoint, name="reports_endpoint_form"),
    path('reports_endpoint/get_form/<uuid:report_id>/', views.reports_endpoint, name="reports_endpoint_form"),
    path('delete_report/<uuid:report_id>/', views.delete_report, name="delete_report"),

    path('report/<uuid:report_id>/', views.report_public_page, name="report_public_page"),

    path('author_endpoint/', views.author_endpoint, name="author_endpoint"),
    path('author_endpoint/<uuid:author_id>/', views.author_endpoint, name="author_endpoint"),
    path('author_endpoint/get_form/', views.author_endpoint, name="author_endpoint_form"),
    path('author_endpoint/get_form/<uuid:author_id>/', views.author_endpoint, name="author_endpoint_form"),
    path('delete_author/<uuid:author_id>/', views.delete_author, name="delete_author"),

    path('advisor_endpoint/', views.advisor_endpoint, name="advisor_endpoint"),
    path('advisor_endpoint/<uuid:author_id>/', views.advisor_endpoint, name="advisor_endpoint"),
    path('advisor_endpoint/get_form/', views.advisor_endpoint, name="advisor_endpoint_form"),
    path('advisor_endpoint/get_form/<uuid:author_id>/', views.advisor_endpoint, name="advisor_endpoint_form"),

    # file management
    path('file/handle/<uuid:report_id>/<str:model>/', file_views.handle_file, name="handle_file"),
    path('file/handle/<uuid:report_id>/<str:model>/<uuid:file_id>/', file_views.handle_file, name="handle_file"),
    path('file/delete/<str:model>/<uuid:file_id>/', file_views.delete_file,  name="delete_file"),
    path('file/display/<str:model>/<uuid:file_id>/', file_views.display_file, name="display_file"),

]

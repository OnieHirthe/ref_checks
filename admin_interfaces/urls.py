from django.urls import path
from admin_interfaces import views, edit_views

urlpatterns = [
    path('participant_list/', views.participant_list, name="participant_list"),
    path('participant_list/<int:year>/', views.participant_list, name="participant_list"),
    path('participant_csv/<int:year>', views.participant_csv, name="participant_csv"),
    path('everything_json/<int:year>', views.everything_json, name="everything_json"),
    path('report_list/', views.report_list, name="report_list"),
    path('report_list/<int:year>/', views.report_list, name="report_list"),
    path('report_csv/<int:year>', views.report_csv, name="report_csv"),
    
    path('subsection_list/', views.subsection_list, name="subsection_list"),
    path('broadcast_section_list/', views.broadcast_section_list, name="broadcast_section_list"),
    path('black_list/', views.black_list, name="black_list"),
    path('profile/<uuid:profile_id>/', views.profile_view, name="admin_profile"),
    path('report/<uuid:report_id>/', views.report_view, name="admin_report"),

    # subsection work - edits users.models.Subsection
    path('subsection/<uuid:section_id>/', edit_views.handle_subsection, name="handle_subsection"),
    path('subsection/<uuid:section_id>/form/', edit_views.handle_subsection, name="handle_subsection_form"),
    path('subsection/<uuid:section_id>/<uuid:subsection_id>/', edit_views.handle_subsection, name="handle_subsection"),
    path('subsection/<uuid:section_id>/form/<uuid:subsection_id>/', edit_views.handle_subsection, name="handle_subsection_form"),
    path('subsection/delete/<uuid:subsection_id>/', edit_views.delete_subsection, name="delete_subsection"),

    # section broadcast links - edits users.models.Section
    path('section_broadcast/<uuid:section_id>/', edit_views.handle_section_broadcast_link, name="handle_section_broadcast"),

    # black_listed enpoints 
    path('black_listed/', views.black_list_entry, name="handle_bl_entry"),
    path('black_listed/<uuid:bl_id>/', views.black_list_entry, name="handle_bl_entry"),
    path('black_listed/delete/<uuid:bl_id>/', views.bl_entry_delete, name="delete_bl_entry"),
    path('black_listed_user/', views.black_listed_user_endpoint, name="bl_user_endpoint"),
        

    # report section and subsection - edits user.models.Report
    path('attach/section/<uuid:report_id>/', edit_views.report_attach_section, name="report_attach_section"),
    path('attach/section/<uuid:report_id>/form', edit_views.report_attach_section, name="report_attach_section_form"),
    path('attach/subsection/<uuid:report_id>/', edit_views.report_attach_subsection, name="report_attach_subsection"),
    path('attach/subsection/<uuid:report_id>/form', edit_views.report_attach_subsection, name="report_attach_subsection_form"),
   
    # report field editing for user.models.Report fields not standartized yet
    path('report/edit/<uuid:report_id>/has_advisor/', edit_views.admin_report_has_advisor,  name="admin_report_has_advisor"),
    path('report/edit/<uuid:report_id>/attach_authors/', edit_views.admin_report_attach_authors,  name="admin_report_attach_authors"),

    # report status - edits user.models.Report sttaus field
    path('report/status/<uuid:report_id>/', edit_views.set_report_status, name="report_status_review"),
    path('report/status/<uuid:report_id>/accept/', edit_views.set_report_status, { 'status' : "accepted" }, name="report_status_accept"),
    path('report/status/<uuid:report_id>/decline/', edit_views.set_report_status, { 'status' : "declined" }, name="report_status_decline"),

    #report chat
    path('report/chat/<uuid:report_id>/', views.report_chat, name="report_chat"),
    path('report/chat/<uuid:report_id>/form/', views.report_chat, name="report_chat_form"),
    path('report/chat/<uuid:report_id>/form/<uuid:comment_id>/', views.report_chat, name="report_chat_form"),
    path('report/chat/delete/<uuid:comment_id>/', views.del_chat_comment, name="del_chat_comment"),
    
]

# for report field-by-field editing, *almost* standartized
for field in ['abstract', 'lang', 'title', 'plenary', 'pub_link']:
    # no-form version
    urlpatterns.append(
        path(
            f"report/edit/<uuid:report_id>/{field}/", edit_views.admin_report_field, {"field" : field}, name=f"admin_report_{field}"
        ))
    # form-version
    urlpatterns.append(
        path(
            f"report/edit/<uuid:report_id>/{field}/form", edit_views.admin_report_field, {"field" : field}, name=f"admin_report_{field}_form"
        ))


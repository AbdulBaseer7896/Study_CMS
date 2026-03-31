# myapp/Urls/Application_urls.py
from django.urls import path
from myapp.Views.Application_views import (
    create_application,
    get_all_applications,
    get_application,
    update_application,
    delete_application,
    add_module,
    delete_module,
    upload_extra_image,
    delete_extra_image,
    get_student_applications,
)

urlpatterns = [
    # ── Core CRUD ────────────────────────────────────────────────────
    path('applications/',                           create_application,         name='create_application'),
    path('applications/all/',                       get_all_applications,       name='get_all_applications'),
    path('applications/<int:application_id>/',      get_application,            name='get_application'),
    path('applications/<int:application_id>/update/', update_application,       name='update_application'),
    path('applications/<int:application_id>/delete/', delete_application,       name='delete_application'),

    # ── Modules ───────────────────────────────────────────────────────
    path('applications/<int:application_id>/modules/add/',    add_module,       name='add_module'),
    path('applications/modules/<int:module_id>/delete/',      delete_module,    name='delete_module'),

    # ── Extra Images ──────────────────────────────────────────────────
    path('applications/<int:application_id>/images/upload/',  upload_extra_image,  name='upload_extra_image'),
    path('applications/images/<int:image_id>/delete/',        delete_extra_image,  name='delete_extra_image'),

    # ── By Student ────────────────────────────────────────────────────
    path('applications/student/<int:student_id>/',  get_student_applications,   name='get_student_applications'),
]



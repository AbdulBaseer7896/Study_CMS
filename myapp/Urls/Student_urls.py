# myapp/Urls/Student_urls.py
from django.urls import path
from myapp.Views.Auth_views import me_update
from myapp.Views.Student_views import (
    student_my_applications, student_get_application,
    student_my_documents,
    student_identity_documents, student_matric_documents,
    student_inter_documents, student_bs_documents,
    student_ms_documents, student_professional_documents,
    student_upload_experience_letter, student_upload_reference_letter, student_upload_other_document,
    student_delete_experience_letter, student_delete_reference_letter, student_delete_other_document,
    student_delete_grouped_field,
)

urlpatterns = [
    # ── Applications (read-only) ──────────────────────────────────────
    path('student/applications/',                         student_my_applications,   name='student_my_applications'),
    path('student/applications/<int:application_id>/',   student_get_application,   name='student_get_application'),

    # ── Documents (read) ──────────────────────────────────────────────
    path('student/documents/',                            student_my_documents,      name='student_my_documents'),

    # ── Documents (upload / replace within 15 min) ────────────────────
    path('student/documents/identity/',                   student_identity_documents,     name='student_identity'),
    path('student/documents/matric/',                     student_matric_documents,       name='student_matric'),
    path('student/documents/inter/',                      student_inter_documents,        name='student_inter'),
    path('student/documents/bs/',                         student_bs_documents,           name='student_bs'),
    path('student/documents/ms/',                         student_ms_documents,           name='student_ms'),
    path('student/documents/professional/',               student_professional_documents, name='student_professional'),

    # ── Multi-entry uploads ───────────────────────────────────────────
    path('student/documents/experience-letter/',          student_upload_experience_letter,  name='student_upload_exp'),
    path('student/documents/reference-letter/',           student_upload_reference_letter,   name='student_upload_ref'),
    path('student/documents/other/',                      student_upload_other_document,     name='student_upload_other'),

    # ── Multi-entry deletes (within 15 min) ───────────────────────────
    path('student/documents/experience-letter/<int:record_id>/delete/', student_delete_experience_letter, name='student_del_exp'),
    path('student/documents/reference-letter/<int:record_id>/delete/',  student_delete_reference_letter,  name='student_del_ref'),
    path('student/documents/other/<int:record_id>/delete/',             student_delete_other_document,    name='student_del_other'),

    # ── Grouped field delete (within 15 min) ──────────────────────────
    path('student/documents/field/<str:field_name>/delete/', student_delete_grouped_field, name='student_del_field'),
]

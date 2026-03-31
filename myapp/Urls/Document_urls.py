# myapp/Urls/Document_urls.py
from django.urls import path
from myapp.Views.Document_views import (
    identity_documents,
    matric_documents,
    inter_documents,
    bs_documents,
    ms_documents,
    professional_documents,
    upload_experience_letter,
    upload_reference_letter,
    upload_other_document,
    get_student_documents,
    
    delete_grouped_document_field,
    delete_experience_letter,
    delete_reference_letter,
    delete_other_document,
)




urlpatterns = [
    # ── Grouped Document APIs ────────────────────────────────────────
    path('documents/<int:student_id>/identity/',      identity_documents,       name='identity_documents'),
    path('documents/<int:student_id>/matric/',        matric_documents,         name='matric_documents'),
    path('documents/<int:student_id>/inter/',         inter_documents,          name='inter_documents'),
    path('documents/<int:student_id>/bs/',            bs_documents,             name='bs_documents'),
    path('documents/<int:student_id>/ms/',            ms_documents,             name='ms_documents'),
    path('documents/<int:student_id>/professional/',  professional_documents,   name='professional_documents'),

    # ── NEW: Delete a single field from a grouped document ──────────
    path('documents/<int:student_id>/field/<str:field_name>/delete/',
         delete_grouped_document_field, name='delete_grouped_document_field'),

    # ── Multiple Entry APIs ──────────────────────────────────────────
    path('documents/<int:student_id>/experience-letter/', upload_experience_letter, name='upload_experience_letter'),
    path('documents/<int:student_id>/reference-letter/',  upload_reference_letter,  name='upload_reference_letter'),
    path('documents/<int:student_id>/other/',             upload_other_document,    name='upload_other_document'),

    # ── NEW: Delete multi-entry records ─────────────────────────────
    path('documents/experience-letter/<int:record_id>/delete/', delete_experience_letter, name='delete_experience_letter'),
    path('documents/reference-letter/<int:record_id>/delete/',  delete_reference_letter,  name='delete_reference_letter'),
    path('documents/other/<int:record_id>/delete/',             delete_other_document,    name='delete_other_document'),

    # ── Get All Documents ────────────────────────────────────────────
    path('documents/<int:student_id>/',               get_student_documents,    name='get_student_documents'),
]


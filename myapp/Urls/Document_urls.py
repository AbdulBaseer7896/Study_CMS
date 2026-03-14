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

# urlpatterns = [
#     # ── Grouped Document APIs ────────────────────────────────────────
#     path('documents/<int:student_id>/identity/',      identity_documents,       name='identity_documents'),
#     path('documents/<int:student_id>/matric/',        matric_documents,         name='matric_documents'),
#     path('documents/<int:student_id>/inter/',         inter_documents,          name='inter_documents'),
#     path('documents/<int:student_id>/bs/',            bs_documents,             name='bs_documents'),
#     path('documents/<int:student_id>/ms/',            ms_documents,             name='ms_documents'),
#     path('documents/<int:student_id>/professional/',  professional_documents,   name='professional_documents'),

#     # ── Multiple Entry APIs ──────────────────────────────────────────
#     path('documents/<int:student_id>/experience-letter/', upload_experience_letter, name='upload_experience_letter'),
#     path('documents/<int:student_id>/reference-letter/',  upload_reference_letter,  name='upload_reference_letter'),
#     path('documents/<int:student_id>/other/',             upload_other_document,    name='upload_other_document'),

#     # ── Get All Documents ────────────────────────────────────────────
#     path('documents/<int:student_id>/',               get_student_documents,    name='get_student_documents'),
# ]


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







# Here's the complete Postman testing guide for all document APIs.

# Setup — Before Testing
# Login first to get token:
# POST {{study_cms}}login/
# json{
#     "email": "admin@test.com",
#     "password": "admin123"
# }
# Copy access_token and set in every request:

# Authorization → Bearer Token → paste token


# API 1 — Identity Documents
# POST {{study_cms}}api/v1/documents/4/identity/

# Body → form-data

# KEYTYPEVALUEcnic_frontFile← pick imagecnic_backFile← pick imagefather_cnic_frontFile← pick imagefather_cnic_backFile← pick imagepassport_page1File← pick imagepassport_page2File← pick imageb_form_frontFile← pick imageb_form_backFile← pick imagedomicileFile← pick image

# ✅ You don't need to send all fields — send only what you have, rest stay null

# ✅ Expected:
# json{
#     "status": "success",
#     "message": "Identity documents updated successfully",
#     "data": {
#         "cnic_front_url": "https://res.cloudinary.com/...",
#         "cnic_back_url": "https://res.cloudinary.com/...",
#         "father_cnic_front_url": null,
#         ...
#     }
# }

# API 2 — Matric Documents (Class 9 & 10)
# POST {{study_cms}}api/v1/documents/4/matric/

# Body → form-data

# KEYTYPEVALUEmatric_degree_frontFile← pick imagematric_degree_backFile← pick imagematric_result_card_frontFile← pick imagematric_result_card_backFile← pick imagematric_instituteTextPunjab Board Lahorematric_yearText2018matric_descriptionTextOptional notes

# API 3 — Inter Documents (Class 11 & 12)
# POST {{study_cms}}api/v1/documents/4/inter/

# Body → form-data

# KEYTYPEVALUEinter_degree_frontFile← pick imageinter_degree_backFile← pick imageinter_result_card_frontFile← pick imageinter_result_card_backFile← pick imageinter_instituteTextBISE Lahoreinter_yearText2020inter_descriptionTextOptional notes

# API 4 — BS Documents
# POST {{study_cms}}api/v1/documents/4/bs/

# Body → form-data

# KEYTYPEVALUEbs_degree_frontFile← pick imagebs_degree_backFile← pick imagebs_transcript_frontFile← pick imagebs_transcript_backFile← pick imagebs_instituteTextFAST Universitybs_yearText2024bs_descriptionTextComputer Science

# API 5 — MS Documents
# POST {{study_cms}}api/v1/documents/4/ms/

# Body → form-data

# KEYTYPEVALUEms_degree_frontFile← pick imagems_degree_backFile← pick imagems_transcript_frontFile← pick imagems_transcript_backFile← pick imagems_instituteTextLUMSms_yearText2026ms_descriptionTextData Science

# API 6 — Professional Documents
# POST {{study_cms}}api/v1/documents/4/professional/

# Body → form-data

# KEYTYPEVALUEcvFile← pick PDF or imageielts_pteFile← pick imageielts_pte_yearText2024ielts_pte_descriptionTextScore: 7.0

# API 7 — Experience Letter (can upload multiple)
# POST {{study_cms}}api/v1/documents/4/experience-letter/

# Body → form-data

# KEYTYPEVALUEfileFile← pick PDF or imageorganizationTextBitnext TechnologiesyearText2023descriptionText1 year experience

# ✅ Hit this endpoint multiple times to add more experience letters


# API 8 — Reference Letter (can upload multiple)
# POST {{study_cms}}api/v1/documents/4/reference-letter/

# Body → form-data

# KEYTYPEVALUEfileFile← pick PDF or imagereferee_nameTextDr. Ahmed KhanyearText2024descriptionTextProfessor reference

# API 9 — Other Documents (can upload multiple)
# POST {{study_cms}}api/v1/documents/4/other/

# Body → form-data

# KEYTYPEVALUEfileFile← pick any filedocument_nameTextAWS CertificateyearText2024descriptionTextCloud practitioner

# API 10 — Get All Documents
# GET {{study_cms}}api/v1/documents/4/

# No body needed
# Authorization → Bearer Token only

# ✅ Expected response shows everything grouped:
# json{
#     "status": "success",
#     "student": "Ali Hassan",
#     "documents": {
#         "identity": {
#             "cnic_front_url": "https://res.cloudinary.com/...",
#             "cnic_back_url": "https://res.cloudinary.com/...",
#             ...
#         },
#         "matric": {
#             "matric_degree_front_url": "https://res.cloudinary.com/...",
#             "matric_institute": "Punjab Board Lahore",
#             ...
#         },
#         "inter": { ... },
#         "bs": { ... },
#         "ms": { ... },
#         "professional": { ... },
#         "experience_letters": [ {...}, {...} ],
#         "reference_letters":  [ {...} ],
#         "other_documents":    [ {...}, {...} ]
#     }
# }
# ```

# ---

# ## Common Errors

# | Error | Reason | Fix |
# |-------|--------|-----|
# | `403 Forbidden` | Using student token | Use admin or consultant token |
# | `404 Student not found` | Wrong student ID in URL | Check student ID from get users API |
# | `400 Bad Request` | Sending raw JSON | Switch to **form-data** in Postman |
# | File not uploading | Key type is Text not File | Click dropdown next to key → select **File** |

# ---

# ## Quick Checklist
# ```
# ✅ Token from admin or consultant login
# ✅ Body type is form-data (NOT raw JSON)
# ✅ File fields have type File selected (not Text)
# ✅ Student ID in URL belongs to a student role user
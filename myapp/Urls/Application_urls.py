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










# Postman Testing Guide
# Step 1 — Get Tokens
# Admin Login — POST {{study_cms}}login/
# json{ "email": "admin@test.com", "password": "admin123" }
# 📋 Save as Admin Token
# Consultant Login — POST {{study_cms}}login/
# json{ "email": "consultant@test.com", "password": "consult123" }
# 📋 Save as Consultant Token

# API 1 — Create Application
# POST {{study_cms}}api/v1/applications/
# Authorization → Bearer → Admin or Consultant Token
# Body → raw → JSON:
# json{
#     "student": 4,
#     "application_name": "FAST University Application",
#     "country": "Pakistan",
#     "university": "FAST National University",
#     "city": "Lahore",
#     "university_portal_link": "https://admission.fast.edu.pk",
#     "portal_login_id": "student@fast.edu.pk",
#     "portal_login_password": "portal123",
#     "degree_name": "MS Computer Science",
#     "course_title": "MS CS — Artificial Intelligence",
#     "apply_fee": "5000.00",
#     "yearly_fee": "150000.00",
#     "last_date_to_apply": "2026-04-30",
#     "last_date_fee_submit": "2026-05-15",
#     "expected_offer_date": "2026-06-01",
#     "status": "draft",
#     "modules": [
#         { "module_name": "Machine Learning", "description": "Core ML algorithms" },
#         { "module_name": "Deep Learning", "description": "Neural networks" },
#         { "module_name": "Computer Vision", "description": "Image processing" }
#     ]
# }
# ✅ Expected:
# json{
#     "status": "success",
#     "message": "Application created successfully",
#     "application": {
#         "id": 1,
#         "student_name": "Ali Hassan",
#         "university": "FAST National University",
#         "modules": [
#             { "id": 1, "module_name": "Machine Learning" },
#             { "id": 2, "module_name": "Deep Learning" },
#             { "id": 3, "module_name": "Computer Vision" }
#         ],
#         "status": "draft"
#     }
# }

# API 2 — Get All Applications
# GET {{study_cms}}api/v1/applications/all/
# Authorization → Bearer → Admin or Consultant Token
# Optional filters via Params tab:
# KEYVALUEstatusdraftstudent4page1page_size5

# API 3 — Get Single Application
# GET {{study_cms}}api/v1/applications/1/
# Authorization → Bearer → Admin or Consultant Token
# ✅ Returns full detail with modules and extra images

# API 4 — Update Application
# PATCH {{study_cms}}api/v1/applications/1/update/
# Authorization → Bearer → Admin or Consultant Token
# Body → form-data (use form-data because we may send files):
# KEYTYPEVALUEstatusTextappliedoffer_letterFile← pick PDFfee_slipFile← pick imageexpected_offer_dateText2026-07-01portal_login_passwordTextnewpassword123

# ✅ Send only the fields you want to update


# API 5 — Delete Application (Admin only)
# DELETE {{study_cms}}api/v1/applications/1/delete/
# Authorization → Bearer → Admin Token only

# No body needed

# ✅ Expected:
# json{
#     "status": "success",
#     "message": "Application 'FAST University Application' deleted successfully"
# }
# ❌ With Consultant Token:
# json{
#     "error": "Permission denied. Only admin can delete applications."
# }

# API 6 — Add Module
# POST {{study_cms}}api/v1/applications/1/modules/add/
# Authorization → Bearer → Admin or Consultant Token
# Body → raw → JSON:
# json{
#     "module_name": "Natural Language Processing",
#     "description": "Text processing and analysis"
# }

# API 7 — Delete Module (Admin only)
# DELETE {{study_cms}}api/v1/applications/modules/1/delete/
# Authorization → Bearer → Admin Token only

# No body needed


# API 8 — Upload Extra Image
# POST {{study_cms}}api/v1/applications/1/images/upload/
# Authorization → Bearer → Admin or Consultant Token
# Body → form-data:
# KEYTYPEVALUEimageFile← pick any image/PDFcaptionTextFee receipt screenshot

# ✅ Hit multiple times to upload more images


# API 9 — Delete Extra Image (Admin only)
# DELETE {{study_cms}}api/v1/applications/images/1/delete/
# Authorization → Bearer → Admin Token only

# No body needed


# API 10 — Get Student's All Applications
# GET {{study_cms}}api/v1/applications/student/4/
# Authorization → Bearer → Admin or Consultant Token
# ✅ Returns all applications for student ID 4

# Permissions Summary
# APIAdminConsultantCreate application✅✅View all applications✅ All✅ Their students onlyView single application✅✅Update application✅✅Delete application✅❌Add module✅✅Delete module✅❌Upload extra image✅✅Delete extra image✅❌View student applications✅✅
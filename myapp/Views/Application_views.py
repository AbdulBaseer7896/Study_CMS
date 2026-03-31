# # # myapp/Views/Application_views.py
# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.pagination import PageNumberPagination
# # from myapp.Models.Auth_models import User
# # from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
# # from myapp.serializers.Application_serializers import (
# #     ApplicationCreateSerializer, ApplicationUpdateSerializer,
# #     ApplicationDetailSerializer, ApplicationListSerializer,
# #     ApplicationModuleSerializer, ApplicationImageSerializer,
# # )
# # import json


# # def has_access(user):
# #     return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]

# # def is_admin(user):
# #     return user.role == User.Role.ADMIN


# # # ── CREATE APPLICATION ────────────────────────────────────────────────
# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def create_application(request):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)

# #     data = request.data.copy()
# #     if 'modules' in data and isinstance(data['modules'], str):
# #         try:
# #             data['modules'] = json.loads(data['modules'])
# #         except json.JSONDecodeError:
# #             return Response({"error": "modules must be a valid JSON array"}, status=400)

# #     serializer = ApplicationCreateSerializer(data=data, context={'request': request})
# #     if serializer.is_valid():
# #         application = serializer.save(created_by=request.user, updated_by=request.user)

# #         # Send email notification in background
# #         from myapp.Utils.email_tasks import send_application_created_task
# #         send_application_created_task.delay(application.id)

# #         return Response({
# #             "status": "success",
# #             "message": "Application created successfully",
# #             "application": ApplicationDetailSerializer(application, context={'request': request}).data
# #         }, status=201)
# #     return Response(serializer.errors, status=400)


# # # ── GET ALL APPLICATIONS ──────────────────────────────────────────────
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_all_applications(request):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)

# #     if request.user.role == User.Role.ADMIN:
# #         applications = Application.objects.all()
# #     else:
# #         applications = Application.objects.filter(student__assigned_to=request.user)

# #     status_filter = request.query_params.get('status')
# #     if status_filter:
# #         applications = applications.filter(status=status_filter)

# #     student_id = request.query_params.get('student')
# #     if student_id:
# #         applications = applications.filter(student_id=student_id)

# #     applications = applications.order_by('-created_at')

# #     paginator = PageNumberPagination()
# #     paginator.page_size = 10
# #     paginator.page_size_query_param = 'page_size'
# #     paginated  = paginator.paginate_queryset(applications, request)
# #     serializer = ApplicationListSerializer(paginated, many=True, context={'request': request})
# #     return paginator.get_paginated_response({"status": "success", "total": applications.count(), "applications": serializer.data})


# # # ── GET SINGLE APPLICATION ────────────────────────────────────────────
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_application(request, application_id):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)
# #     try:
# #         application = Application.objects.get(id=application_id)
# #     except Application.DoesNotExist:
# #         return Response({"error": "Application not found."}, status=404)
# #     return Response({"status": "success", "application": ApplicationDetailSerializer(application, context={'request': request}).data})


# # # ── UPDATE APPLICATION ────────────────────────────────────────────────
# # @api_view(['PATCH'])
# # @permission_classes([IsAuthenticated])
# # def update_application(request, application_id):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)
# #     try:
# #         application = Application.objects.get(id=application_id)
# #     except Application.DoesNotExist:
# #         return Response({"error": "Application not found."}, status=404)

# #     # Track which fields changed for the email
# #     trackable = ['status', 'apply_fee', 'yearly_fee', 'last_date_to_apply',
# #                  'last_date_fee_submit', 'expected_offer_date', 'offer_letter', 'fee_slip']
# #     changed_fields = {}
# #     for field in trackable:
# #         if field in request.data:
# #             old_val = str(getattr(application, field) or '—')
# #             new_val = str(request.data[field])
# #             if old_val != new_val:
# #                 label = field.replace('_', ' ').title()
# #                 changed_fields[label] = new_val

# #     serializer = ApplicationUpdateSerializer(application, data=request.data, partial=True, context={'request': request})
# #     if serializer.is_valid():
# #         serializer.save(updated_by=request.user)

# #         # Send update email in background
# #         if changed_fields:
# #             from myapp.Utils.email_tasks import send_application_updated_task
# #             send_application_updated_task.delay(application.id, changed_fields, request.user.name)

# #         return Response({"status": "success", "message": "Application updated successfully", "application": serializer.data})
# #     return Response(serializer.errors, status=400)


# # # ── DELETE APPLICATION ────────────────────────────────────────────────
# # @api_view(['DELETE'])
# # @permission_classes([IsAuthenticated])
# # def delete_application(request, application_id):
# #     if not is_admin(request.user):
# #         return Response({"error": "Permission denied. Only admin can delete applications."}, status=403)
# #     try:
# #         application = Application.objects.get(id=application_id)
# #     except Application.DoesNotExist:
# #         return Response({"error": "Application not found."}, status=404)
# #     name = application.application_name
# #     application.delete()
# #     return Response({"status": "success", "message": f"Application '{name}' deleted successfully"})


# # # ── ADD MODULE ────────────────────────────────────────────────────────
# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def add_module(request, application_id):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)
# #     try:
# #         application = Application.objects.get(id=application_id)
# #     except Application.DoesNotExist:
# #         return Response({"error": "Application not found."}, status=404)
# #     serializer = ApplicationModuleSerializer(data=request.data)
# #     if serializer.is_valid():
# #         serializer.save(application=application)
# #         return Response({"status": "success", "message": "Module added successfully", "module": serializer.data}, status=201)
# #     return Response(serializer.errors, status=400)


# # # ── DELETE MODULE ─────────────────────────────────────────────────────
# # @api_view(['DELETE'])
# # @permission_classes([IsAuthenticated])
# # def delete_module(request, module_id):
# #     if not is_admin(request.user):
# #         return Response({"error": "Permission denied. Only admin can delete modules."}, status=403)
# #     try:
# #         module = ApplicationModule.objects.get(id=module_id)
# #     except ApplicationModule.DoesNotExist:
# #         return Response({"error": "Module not found."}, status=404)
# #     module.delete()
# #     return Response({"status": "success", "message": "Module deleted successfully"})


# # # ── UPLOAD EXTRA IMAGE ────────────────────────────────────────────────
# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def upload_extra_image(request, application_id):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)
# #     try:
# #         application = Application.objects.get(id=application_id)
# #     except Application.DoesNotExist:
# #         return Response({"error": "Application not found."}, status=404)
# #     serializer = ApplicationImageSerializer(data=request.data, context={'request': request})
# #     if serializer.is_valid():
# #         serializer.save(application=application, uploaded_by=request.user)
# #         return Response({"status": "success", "message": "Image uploaded successfully", "image": serializer.data}, status=201)
# #     return Response(serializer.errors, status=400)


# # # ── DELETE EXTRA IMAGE ────────────────────────────────────────────────
# # @api_view(['DELETE'])
# # @permission_classes([IsAuthenticated])
# # def delete_extra_image(request, image_id):
# #     if not is_admin(request.user):
# #         return Response({"error": "Permission denied. Only admin can delete images."}, status=403)
# #     try:
# #         image = ApplicationImage.objects.get(id=image_id)
# #     except ApplicationImage.DoesNotExist:
# #         return Response({"error": "Image not found."}, status=404)
# #     image.image.delete(save=False)
# #     image.delete()
# #     return Response({"status": "success", "message": "Image deleted successfully"})


# # # ── GET STUDENT APPLICATIONS ──────────────────────────────────────────
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_student_applications(request, student_id):
# #     if not has_access(request.user):
# #         return Response({"error": "Permission denied."}, status=403)
# #     try:
# #         student = User.objects.get(id=student_id, role=User.Role.STUDENT)
# #     except User.DoesNotExist:
# #         return Response({"error": "Student not found."}, status=404)
# #     applications = Application.objects.filter(student=student).order_by('-created_at')
# #     serializer = ApplicationDetailSerializer(applications, many=True, context={'request': request})
# #     return Response({"status": "success", "student": student.name, "total_applications": applications.count(), "applications": serializer.data})






# # myapp/Views/Application_views.py
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.pagination import PageNumberPagination
# from myapp.Models.Auth_models import User
# from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
# from myapp.serializers.Application_serializers import (
#     ApplicationCreateSerializer, ApplicationUpdateSerializer,
#     ApplicationDetailSerializer, ApplicationListSerializer,
#     ApplicationModuleSerializer, ApplicationImageSerializer,
# )
# import json


# def has_access(user):
#     return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]

# def is_admin(user):
#     return user.role == User.Role.ADMIN


# # ── CREATE APPLICATION ────────────────────────────────────────────────
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_application(request):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)

#     data = request.data.copy()
#     if 'modules' in data and isinstance(data['modules'], str):
#         try:
#             data['modules'] = json.loads(data['modules'])
#         except json.JSONDecodeError:
#             return Response({"error": "modules must be a valid JSON array"}, status=400)

#     # Auto-correct common status typos before validation
#     VALID_STATUSES = ['draft','applied','under_review','offer_received','accepted','rejected','withdrawn','enrolled']
#     if 'status' in data and data['status'] not in VALID_STATUSES:
#         data['status'] = 'draft'

#     serializer = ApplicationCreateSerializer(data=data, context={'request': request})
#     if serializer.is_valid():
#         application = serializer.save(created_by=request.user, updated_by=request.user)

#         # Send email notification in background
#         from myapp.Utils.email_tasks import send_application_created_task
#         send_application_created_task.delay(application.id)

#         return Response({
#             "status": "success",
#             "message": "Application created successfully",
#             "application": ApplicationDetailSerializer(application, context={'request': request}).data
#         }, status=201)
#     return Response(serializer.errors, status=400)


# # ── GET ALL APPLICATIONS ──────────────────────────────────────────────
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_all_applications(request):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)

#     if request.user.role == User.Role.ADMIN:
#         applications = Application.objects.all()
#     else:
#         applications = Application.objects.filter(student__assigned_to=request.user)

#     status_filter = request.query_params.get('status')
#     if status_filter:
#         applications = applications.filter(status=status_filter)

#     student_id = request.query_params.get('student')
#     if student_id:
#         applications = applications.filter(student_id=student_id)

#     applications = applications.order_by('-created_at')

#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     paginator.page_size_query_param = 'page_size'
#     paginated  = paginator.paginate_queryset(applications, request)
#     serializer = ApplicationListSerializer(paginated, many=True, context={'request': request})
#     return paginator.get_paginated_response({"status": "success", "total": applications.count(), "applications": serializer.data})


# # ── GET SINGLE APPLICATION ────────────────────────────────────────────
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_application(request, application_id):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found."}, status=404)
#     return Response({"status": "success", "application": ApplicationDetailSerializer(application, context={'request': request}).data})


# # ── UPDATE APPLICATION ────────────────────────────────────────────────
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def update_application(request, application_id):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found."}, status=404)

#     # Track which fields changed for the email
#     trackable = ['status', 'apply_fee', 'yearly_fee', 'last_date_to_apply',
#                  'last_date_fee_submit', 'expected_offer_date', 'offer_letter', 'fee_slip']
#     changed_fields = {}
#     for field in trackable:
#         if field in request.data:
#             old_val = str(getattr(application, field) or '—')
#             new_val = str(request.data[field])
#             if old_val != new_val:
#                 label = field.replace('_', ' ').title()
#                 changed_fields[label] = new_val

#     serializer = ApplicationUpdateSerializer(application, data=request.data, partial=True, context={'request': request})
#     if serializer.is_valid():
#         serializer.save(updated_by=request.user)

#         # Send update email in background
#         if changed_fields:
#             from myapp.Utils.email_tasks import send_application_updated_task
#             send_application_updated_task.delay(application.id, changed_fields, request.user.name)

#         return Response({"status": "success", "message": "Application updated successfully", "application": serializer.data})
#     return Response(serializer.errors, status=400)


# # ── DELETE APPLICATION ────────────────────────────────────────────────
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_application(request, application_id):
#     if not is_admin(request.user):
#         return Response({"error": "Permission denied. Only admin can delete applications."}, status=403)
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found."}, status=404)
#     name = application.application_name
#     application.delete()
#     return Response({"status": "success", "message": f"Application '{name}' deleted successfully"})


# # ── ADD MODULE ────────────────────────────────────────────────────────
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_module(request, application_id):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found."}, status=404)
#     serializer = ApplicationModuleSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(application=application)
#         return Response({"status": "success", "message": "Module added successfully", "module": serializer.data}, status=201)
#     return Response(serializer.errors, status=400)


# # ── DELETE MODULE ─────────────────────────────────────────────────────
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_module(request, module_id):
#     if not is_admin(request.user):
#         return Response({"error": "Permission denied. Only admin can delete modules."}, status=403)
#     try:
#         module = ApplicationModule.objects.get(id=module_id)
#     except ApplicationModule.DoesNotExist:
#         return Response({"error": "Module not found."}, status=404)
#     module.delete()
#     return Response({"status": "success", "message": "Module deleted successfully"})


# # ── UPLOAD EXTRA IMAGE ────────────────────────────────────────────────
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_extra_image(request, application_id):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found."}, status=404)
#     serializer = ApplicationImageSerializer(data=request.data, context={'request': request})
#     if serializer.is_valid():
#         serializer.save(application=application, uploaded_by=request.user)
#         return Response({"status": "success", "message": "Image uploaded successfully", "image": serializer.data}, status=201)
#     return Response(serializer.errors, status=400)


# # ── DELETE EXTRA IMAGE ────────────────────────────────────────────────
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_extra_image(request, image_id):
#     if not is_admin(request.user):
#         return Response({"error": "Permission denied. Only admin can delete images."}, status=403)
#     try:
#         image = ApplicationImage.objects.get(id=image_id)
#     except ApplicationImage.DoesNotExist:
#         return Response({"error": "Image not found."}, status=404)
#     image.image.delete(save=False)
#     image.delete()
#     return Response({"status": "success", "message": "Image deleted successfully"})


# # ── GET STUDENT APPLICATIONS ──────────────────────────────────────────
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_student_applications(request, student_id):
#     if not has_access(request.user):
#         return Response({"error": "Permission denied."}, status=403)
#     try:
#         student = User.objects.get(id=student_id, role=User.Role.STUDENT)
#     except User.DoesNotExist:
#         return Response({"error": "Student not found."}, status=404)
#     applications = Application.objects.filter(student=student).order_by('-created_at')
#     serializer = ApplicationDetailSerializer(applications, many=True, context={'request': request})
#     return Response({"status": "success", "student": student.name, "total_applications": applications.count(), "applications": serializer.data})















# myapp/Views/Application_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from myapp.Models.Auth_models import User
from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
from myapp.serializers.Application_serializers import (
    ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationDetailSerializer, ApplicationListSerializer,
    ApplicationModuleSerializer, ApplicationImageSerializer,
)
import json


def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]

def is_admin(user):
    return user.role == User.Role.ADMIN


# ── CREATE APPLICATION ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_application(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    data = request.data.copy()
    if 'modules' in data and isinstance(data['modules'], str):
        try:
            data['modules'] = json.loads(data['modules'])
        except json.JSONDecodeError:
            return Response({"error": "modules must be a valid JSON array"}, status=400)

    # Auto-correct common status typos before validation
    VALID_STATUSES = ['draft','applied','under_review','offer_received','accepted','rejected','withdrawn','enrolled']
    if 'status' in data and data['status'] not in VALID_STATUSES:
        data['status'] = 'draft'

    serializer = ApplicationCreateSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        application = serializer.save(created_by=request.user, updated_by=request.user)

        # Send email notification in background
        from myapp.Utils.email_tasks import send_application_created_task
        send_application_created_task.delay(application.id)

        return Response({
            "status": "success",
            "message": "Application created successfully",
            "application": ApplicationDetailSerializer(application, context={'request': request}).data
        }, status=201)
    return Response(serializer.errors, status=400)


# ── GET ALL APPLICATIONS ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_applications(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    if request.user.role == User.Role.ADMIN:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(student__assigned_to=request.user)

    status_filter = request.query_params.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    student_id = request.query_params.get('student')
    if student_id:
        applications = applications.filter(student_id=student_id)

    applications = applications.order_by('-created_at')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = 'page_size'
    paginated  = paginator.paginate_queryset(applications, request)
    serializer = ApplicationListSerializer(paginated, many=True, context={'request': request})
    return paginator.get_paginated_response({"status": "success", "total": applications.count(), "applications": serializer.data})


# ── GET SINGLE APPLICATION ────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)
    return Response({"status": "success", "application": ApplicationDetailSerializer(application, context={'request': request}).data})


# ── UPDATE APPLICATION ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)

    # Track non-file field changes BEFORE save
    trackable = ['status', 'apply_fee', 'yearly_fee', 'last_date_to_apply',
                 'last_date_fee_submit', 'expected_offer_date']
    file_fields = ['offer_letter', 'fee_slip']
    changed_fields = {}
    for field in trackable:
        if field in request.data:
            old_val = str(getattr(application, field) or '')
            new_val = str(request.data.get(field, ''))
            if old_val != new_val and new_val:
                changed_fields[field.replace('_', ' ').title()] = new_val

    # Note which file fields are being uploaded
    uploading_files = [f for f in file_fields if f in request.FILES]

    serializer = ApplicationUpdateSerializer(application, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        saved = serializer.save(updated_by=request.user)

        # AFTER save — get actual Cloudinary URLs for uploaded files
        for field in uploading_files:
            file_obj = getattr(saved, field, None)
            if file_obj:
                try:
                    url = file_obj.url
                    # Ensure .pdf extension for Cloudinary raw files
                    if file_obj.name and file_obj.name.lower().endswith('.pdf') and not url.lower().endswith('.pdf'):
                        url = url + '.pdf'
                    label = field.replace('_', ' ').title()
                    changed_fields[label] = url  # plain URL string
                except Exception:
                    changed_fields[field.replace('_', ' ').title()] = 'uploaded'

        # Send update email in background
        if changed_fields:
            from myapp.Utils.email_tasks import send_application_updated_task
            send_application_updated_task.delay(application.id, changed_fields, request.user.name)

        return Response({"status": "success", "message": "Application updated successfully", "application": serializer.data})
    return Response(serializer.errors, status=400)


# ── DELETE APPLICATION ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_application(request, application_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete applications."}, status=403)
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)
    name = application.application_name
    application.delete()
    return Response({"status": "success", "message": f"Application '{name}' deleted successfully"})


# ── ADD MODULE ────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_module(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)
    serializer = ApplicationModuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(application=application)
        return Response({"status": "success", "message": "Module added successfully", "module": serializer.data}, status=201)
    return Response(serializer.errors, status=400)


# ── DELETE MODULE ─────────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_module(request, module_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete modules."}, status=403)
    try:
        module = ApplicationModule.objects.get(id=module_id)
    except ApplicationModule.DoesNotExist:
        return Response({"error": "Module not found."}, status=404)
    module.delete()
    return Response({"status": "success", "message": "Module deleted successfully"})


# ── UPLOAD EXTRA IMAGE ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_extra_image(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)
    serializer = ApplicationImageSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(application=application, uploaded_by=request.user)
        return Response({"status": "success", "message": "Image uploaded successfully", "image": serializer.data}, status=201)
    return Response(serializer.errors, status=400)


# ── DELETE EXTRA IMAGE ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_extra_image(request, image_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete images."}, status=403)
    try:
        image = ApplicationImage.objects.get(id=image_id)
    except ApplicationImage.DoesNotExist:
        return Response({"error": "Image not found."}, status=404)
    image.image.delete(save=False)
    image.delete()
    return Response({"status": "success", "message": "Image deleted successfully"})


# ── GET STUDENT APPLICATIONS ──────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_applications(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)
    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=404)
    applications = Application.objects.filter(student=student).order_by('-created_at')
    serializer = ApplicationDetailSerializer(applications, many=True, context={'request': request})
    return Response({"status": "success", "student": student.name, "total_applications": applications.count(), "applications": serializer.data})
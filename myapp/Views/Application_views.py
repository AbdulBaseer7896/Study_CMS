# myapp/Views/Application_views.py  —  FULLY ASYNC  (100% sync_to_async safe)
"""
Rule: EVERY database access and EVERY serializer.data access must be inside
      a sync_to_async() wrapper. No ORM or serializer calls at the async level.
"""
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from asgiref.sync import sync_to_async
import json

from myapp.Models.Auth_models import User
from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
from myapp.serializers.Application_serializers import (
    ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationDetailSerializer, ApplicationListSerializer,
    ApplicationModuleSerializer, ApplicationImageSerializer,
)

VALID_STATUSES = ['draft', 'applied', 'under_review', 'offer_received',
                  'accepted', 'rejected', 'withdrawn', 'enrolled']


def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]

def is_admin(user):
    return user.role == User.Role.ADMIN


# ── CREATE APPLICATION ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def create_application(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    data = request.data.copy()
    if 'modules' in data and isinstance(data['modules'], str):
        try:
            data['modules'] = json.loads(data['modules'])
        except json.JSONDecodeError:
            return Response({"error": "modules must be a valid JSON array"}, status=400)

    if 'status' in data and data['status'] not in VALID_STATUSES:
        data['status'] = 'draft'

    def _create():
        serializer = ApplicationCreateSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return None, serializer.errors
        application = serializer.save(created_by=request.user, updated_by=request.user)
        detail_serializer = ApplicationDetailSerializer(application, context={'request': request})
        return detail_serializer.data, None

    result, errors = await sync_to_async(_create)()
    if errors:
        return Response(errors, status=400)

    from myapp.Utils.email_tasks import send_application_created_task
    await sync_to_async(send_application_created_task.delay)(result['id'])

    return Response({
        "status": "success",
        "message": "Application created successfully",
        "application": result,
    }, status=201)


# ── GET ALL APPLICATIONS — paginated ─────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_all_applications(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    status_filter = request.query_params.get('status')
    student_id    = request.query_params.get('student')
    search        = request.query_params.get('search', '').strip()
    page_size     = int(request.query_params.get('page_size', 10))
    page_size     = min(max(page_size, 1), 100)

    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100

    def _fetch():
        if request.user.role == User.Role.ADMIN:
            qs = Application.objects.all()
        else:
            qs = Application.objects.filter(student__assigned_to=request.user)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if student_id:
            qs = qs.filter(student_id=student_id)
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(application_name__icontains=search) |
                Q(university__icontains=search) |
                Q(student__name__icontains=search)
            )
        qs    = qs.order_by('-created_at')
        total = qs.count()
        paginated  = paginator.paginate_queryset(qs, request)
        serializer = ApplicationListSerializer(paginated, many=True, context={'request': request})
        return total, serializer.data   # .data safe — inside sync context

    total, data = await sync_to_async(_fetch)()
    return paginator.get_paginated_response({
        "status": "success",
        "total": total,
        "applications": data,
    })


# ── GET SINGLE APPLICATION ────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _fetch():
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None
        serializer = ApplicationDetailSerializer(application, context={'request': request})
        return serializer.data   # .data safe — inside sync context

    data = await sync_to_async(_fetch)()
    if data is None:
        return Response({"error": "Application not found."}, status=404)
    return Response({"status": "success", "application": data})


# ── UPDATE APPLICATION ────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
async def update_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    trackable   = ['status', 'apply_fee', 'yearly_fee', 'last_date_to_apply',
                   'last_date_fee_submit', 'expected_offer_date']
    file_fields = ['offer_letter', 'fee_slip']
    uploading_files = [f for f in file_fields if f in request.FILES]

    def _update():
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None, "not_found", {}, None

        changed_fields = {}
        for field in trackable:
            if field in request.data:
                old_val = str(getattr(application, field) or '')
                new_val = str(request.data.get(field, ''))
                if old_val != new_val and new_val:
                    changed_fields[field.replace('_', ' ').title()] = new_val

        serializer = ApplicationUpdateSerializer(
            application, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return None, "invalid", serializer.errors, None

        saved = serializer.save(updated_by=request.user)

        for field in uploading_files:
            file_obj = getattr(saved, field, None)
            if file_obj:
                try:
                    url = file_obj.url
                    if file_obj.name and file_obj.name.lower().endswith('.pdf') and not url.lower().endswith('.pdf'):
                        url = url + '.pdf'
                    changed_fields[field.replace('_', ' ').title()] = url
                except Exception:
                    changed_fields[field.replace('_', ' ').title()] = 'uploaded'

        return serializer.data, None, {}, changed_fields   # .data safe

    result, err, errors, changed_fields = await sync_to_async(_update)()

    if err == "not_found":
        return Response({"error": "Application not found."}, status=404)
    if err == "invalid":
        return Response(errors, status=400)

    if changed_fields:
        from myapp.Utils.email_tasks import send_application_updated_task
        await sync_to_async(send_application_updated_task.delay)(
            result['id'], changed_fields, request.user.name
        )

    return Response({"status": "success", "message": "Application updated successfully", "application": result})


# ── DELETE APPLICATION ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_application(request, application_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete applications."}, status=403)

    def _delete():
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None
        name = application.application_name
        application.delete()
        return name

    name = await sync_to_async(_delete)()
    if name is None:
        return Response({"error": "Application not found."}, status=404)
    return Response({"status": "success", "message": f"Application '{name}' deleted successfully"})


# ── ADD MODULE ────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def add_module(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _add():
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None, "not_found"
        serializer = ApplicationModuleSerializer(data=request.data)
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(application=application)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_add)()
    if err == "not_found":
        return Response({"error": "Application not found."}, status=404)
    if err == "invalid":
        return Response(result, status=400)
    return Response({"status": "success", "message": "Module added successfully", "module": result}, status=201)


# ── DELETE MODULE ─────────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_module(request, module_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete modules."}, status=403)

    def _delete():
        try:
            module = ApplicationModule.objects.get(id=module_id)
        except ApplicationModule.DoesNotExist:
            return False
        module.delete()
        return True

    found = await sync_to_async(_delete)()
    if not found:
        return Response({"error": "Module not found."}, status=404)
    return Response({"status": "success", "message": "Module deleted successfully"})


# ── UPLOAD EXTRA IMAGE ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_extra_image(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _upload():
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None, "not_found"
        serializer = ApplicationImageSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(application=application, uploaded_by=request.user)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_upload)()
    if err == "not_found":
        return Response({"error": "Application not found."}, status=404)
    if err == "invalid":
        return Response(result, status=400)
    return Response({"status": "success", "message": "Image uploaded successfully", "image": result}, status=201)


# ── DELETE EXTRA IMAGE ────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_extra_image(request, image_id):
    if not is_admin(request.user):
        return Response({"error": "Permission denied. Only admin can delete images."}, status=403)

    def _delete():
        try:
            image = ApplicationImage.objects.get(id=image_id)
        except ApplicationImage.DoesNotExist:
            return False
        image.image.delete(save=False)
        image.delete()
        return True

    found = await sync_to_async(_delete)()
    if not found:
        return Response({"error": "Image not found."}, status=404)
    return Response({"status": "success", "message": "Image deleted successfully"})


# ── GET STUDENT APPLICATIONS ──────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_student_applications(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _fetch():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, None
        qs = Application.objects.filter(student=student).order_by('-created_at')
        serializer = ApplicationDetailSerializer(qs, many=True, context={'request': request})
        return student.name, serializer.data   # .data safe

    result = await sync_to_async(_fetch)()
    if result[0] is None:
        return Response({"error": "Student not found."}, status=404)
    student_name, data = result
    return Response({"status": "success", "student": student_name, "applications": data})

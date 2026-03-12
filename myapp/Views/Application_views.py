# myapp/Views/Application_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from myapp.Models.Auth_models import User
from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
from myapp.serializers.Application_serializers import (
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer,
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    ApplicationModuleSerializer,
    ApplicationImageSerializer,
)
import json


# ── Permission Helper ─────────────────────────────────────────────────
def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]


# ════════════════════════════════════════════════════════════════════
#  API 1 — CREATE APPLICATION
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_application(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    # Handle modules sent as JSON string in form-data
    data = request.data.copy()
    if 'modules' in data and isinstance(data['modules'], str):
        try:
            data['modules'] = json.loads(data['modules'])
        except json.JSONDecodeError:
            return Response({"error": "modules must be a valid JSON array"}, status=400)

    serializer = ApplicationCreateSerializer(
        data=data,
        context={'request': request}
    )
    if serializer.is_valid():
        application = serializer.save(created_by=request.user, updated_by=request.user)
        return Response({
            "status": "success",
            "message": "Application created successfully",
            "application": ApplicationDetailSerializer(
                application, context={'request': request}
            ).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 2 — GET ALL APPLICATIONS
#  Admin: sees all | Consultant: sees their students only
# ════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_applications(request):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    if request.user.role == User.Role.ADMIN:
        applications = Application.objects.all()
    else:
        # Consultant sees only their assigned students' applications
        applications = Application.objects.filter(
            student__assigned_to=request.user
        )

    # Filter by status if provided
    status_filter = request.query_params.get('status', None)
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Filter by student if provided
    student_id = request.query_params.get('student', None)
    if student_id:
        applications = applications.filter(student_id=student_id)

    applications = applications.order_by('-created_at')

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = 'page_size'

    paginated = paginator.paginate_queryset(applications, request)
    serializer = ApplicationListSerializer(paginated, many=True, context={'request': request})

    return paginator.get_paginated_response({
        "status": "success",
        "total": applications.count(),
        "applications": serializer.data
    })


# ════════════════════════════════════════════════════════════════════
#  API 3 — GET SINGLE APPLICATION DETAIL
# ════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationDetailSerializer(application, context={'request': request})
    return Response({
        "status": "success",
        "application": serializer.data
    })


# ════════════════════════════════════════════════════════════════════
#  API 4 — UPDATE APPLICATION
# ════════════════════════════════════════════════════════════════════
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_application(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationUpdateSerializer(
        application, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(updated_by=request.user)
        return Response({
            "status": "success",
            "message": "Application updated successfully",
            "application": serializer.data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 5 — DELETE APPLICATION (Admin only)
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_application(request, application_id):
    # ← Only admin can delete
    if not is_admin(request.user):
        return Response(
            {"error": "Permission denied. Only admin can delete applications."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    name = application.application_name
    application.delete()

    return Response({
        "status": "success",
        "message": f"Application '{name}' deleted successfully"
    })


# ════════════════════════════════════════════════════════════════════
#  API 6 — ADD MODULE to existing application
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_module(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationModuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(application=application)
        return Response({
            "status": "success",
            "message": "Module added successfully",
            "module": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 7 — DELETE MODULE (Admin only)
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_module(request, module_id):
    # ← Only admin can delete
    if not is_admin(request.user):
        return Response(
            {"error": "Permission denied. Only admin can delete modules."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        module = ApplicationModule.objects.get(id=module_id)
    except ApplicationModule.DoesNotExist:
        return Response({"error": "Module not found."}, status=status.HTTP_404_NOT_FOUND)

    module.delete()
    return Response({
        "status": "success",
        "message": "Module deleted successfully"
    })

# ════════════════════════════════════════════════════════════════════
#  API 8 — UPLOAD EXTRA IMAGE
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_extra_image(request, application_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationImageSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(application=application, uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Image uploaded successfully",
            "image": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# ════════════════════════════════════════════════════════════════════
#  API 10 — GET ALL APPLICATIONS OF ONE STUDENT
# ════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_applications(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    applications = Application.objects.filter(student=student).order_by('-created_at')

    serializer = ApplicationDetailSerializer(
        applications, many=True,
        context={'request': request}
    )
    return Response({
        "status": "success",
        "student": student.name,
        "total_applications": applications.count(),
        "applications": serializer.data
    })


# ════════════════════════════════════════════════════════════════════
#  API 9 — DELETE EXTRA IMAGE (Admin only)
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_extra_image(request, image_id):
    # ← Only admin can delete
    if not is_admin(request.user):
        return Response(
            {"error": "Permission denied. Only admin can delete images."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        image = ApplicationImage.objects.get(id=image_id)
    except ApplicationImage.DoesNotExist:
        return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

    image.image.delete(save=False)
    image.delete()

    return Response({
        "status": "success",
        "message": "Image deleted successfully"
    })


# ── Permission Helpers ────────────────────────────────────────────────
def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]

def is_admin(user):
    return user.role == User.Role.ADMIN

def is_consultant(user):
    return user.role == User.Role.CONSULTANT
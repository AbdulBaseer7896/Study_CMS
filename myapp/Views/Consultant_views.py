# myapp/Views/Consultant_views.py  —  FULLY ASYNC (100% sync_to_async safe)
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from asgiref.sync import sync_to_async

from myapp.Models.Auth_models import User
from myapp.serializers.Consultant_serializers import (
    ConsultantCreateStudentSerializer,
    ConsultantUpdateStudentSerializer
)


def is_consultant(user):
    return user.role == User.Role.CONSULTANT

def is_admin(user):
    return user.role == User.Role.ADMIN


@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def consultant_create_student(request):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data = dict(data)
    data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}

    if is_consultant(request.user):
        if not data.get('reference'):
            data['reference'] = request.user.id
        if not data.get('assigned_to'):
            data['assigned_to'] = request.user.id

    def _create():
        serializer = ConsultantCreateStudentSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return None, serializer.errors
        student = serializer.save()
        # Re-serialize for response (avoids re-accessing .data outside sync)
        response_serializer = ConsultantCreateStudentSerializer(student, context={'request': request})
        return response_serializer.data, None   # .data safe

    student_data, errors = await sync_to_async(_create)()
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "success",
        "message": "Student created successfully",
        "student": student_data,
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
async def consultant_update_student(request, student_id):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _update():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, "not_found"
        serializer = ConsultantUpdateStudentSerializer(
            student, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        if 'profile_picture' in request.FILES and student.profile_picture:
            from myapp.Utils.storage_utils import delete_image
            delete_image(student.profile_picture.name)
        serializer.save()
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_update)()
    if err == "not_found":
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    if err == "invalid":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "success",
        "message": "Student updated successfully",
        "student": result,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def consultant_list_students(request):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    search    = request.query_params.get('search', '').strip()
    page_size = int(request.query_params.get('page_size', 10))
    page_size = min(max(page_size, 1), 100)

    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100

    def _fetch():
        from django.db.models import Q
        if is_consultant(request.user):
            qs = User.objects.filter(
                role=User.Role.STUDENT,
                assigned_to=request.user
            ).select_related('reference', 'assigned_to')
        else:
            qs = User.objects.filter(
                role=User.Role.STUDENT
            ).select_related('reference', 'assigned_to')

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))

        qs        = qs.order_by('name')
        count     = qs.count()
        paginated = paginator.paginate_queryset(qs, request)
        serializer = ConsultantUpdateStudentSerializer(paginated, many=True)
        return count, serializer.data   # .data safe

    count, data = await sync_to_async(_fetch)()
    return paginator.get_paginated_response({
        "status": "success",
        "count": count,
        "students": data,
    })

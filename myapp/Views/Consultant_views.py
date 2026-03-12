# myapp/Views/Consultant_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
def consultant_create_student(request):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response(
            {"error": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN
        )

    # DEBUG — check who is logged in
    # print("=== DEBUG ===")
    # print("Logged in user ID:", request.user.id)
    # print("Logged in user role:", request.user.role)
    # print("is_consultant:", is_consultant(request.user))
    # print("is_admin:", is_admin(request.user))

    data = request.data.copy()
    data = dict(data)
    data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}

    print("Data before auto-assign:", data)

    if is_consultant(request.user):
        if not data.get('reference'):
            data['reference'] = request.user.id
        if not data.get('assigned_to'):
            data['assigned_to'] = request.user.id

    print("Data after auto-assign:", data)
    print("=============")

    serializer = ConsultantCreateStudentSerializer(data=data)
    if serializer.is_valid():
        student = serializer.save()
        return Response({
            "status": "success",
            "message": "Student created successfully",
            "student": ConsultantCreateStudentSerializer(student).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def consultant_update_student(request, student_id):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response(
            {"error": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ConsultantUpdateStudentSerializer(
        student, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Student updated successfully",
            "student": serializer.data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def consultant_list_students(request):
#     if not (is_consultant(request.user) or is_admin(request.user)):
#         return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

#     if is_consultant(request.user):
#         students = User.objects.filter(
#             role=User.Role.STUDENT,
#             assigned_to=request.user
#         )
#     else:
#         students = User.objects.filter(role=User.Role.STUDENT)

#     serializer = ConsultantUpdateStudentSerializer(students, many=True)
#     return Response({
#         "status": "success",
#         "count": students.count(),
#         "students": serializer.data
#     })




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultant_list_students(request):
    if not (is_consultant(request.user) or is_admin(request.user)):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    if is_consultant(request.user):
        # Only students where this consultant is assigned_to
        students = User.objects.filter(
            role=User.Role.STUDENT,
            assigned_to=request.user  # ← strict filter, only their students
        ).select_related('reference', 'assigned_to')  # optimizes DB queries
    else:
        # Admin sees everyone
        students = User.objects.filter(
            role=User.Role.STUDENT
        ).select_related('reference', 'assigned_to')

    serializer = ConsultantUpdateStudentSerializer(students, many=True)
    return Response({
        "status": "success",
        "count": students.count(),
        "students": serializer.data
    })
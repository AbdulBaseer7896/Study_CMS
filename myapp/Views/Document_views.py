# myapp/Views/Document_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from myapp.Models.Auth_models import User
from myapp.Models.Document_models import (
    StudentDocument, ExperienceLetter,
    ReferenceLetter, OtherDocument
)
from myapp.serializers.Document_serializers import (
    IdentityDocumentSerializer,
    MatricDocumentSerializer,
    InterDocumentSerializer,
    BSDocumentSerializer,
    MSDocumentSerializer,
    ProfessionalDocumentSerializer,
    ExperienceLetterSerializer,
    ReferenceLetterSerializer,
    OtherDocumentSerializer,
    StudentAllDocumentsSerializer,
)


# ── Permission Helper ─────────────────────────────────────────────────
def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]


# ── Shared: get or create StudentDocument record for student ──────────
def get_or_create_document_record(student_id):
    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return None, None

    doc, _ = StudentDocument.objects.get_or_create(student=student)
    return student, doc


# ════════════════════════════════════════════════════════════════════
#  API 1 — IDENTITY DOCUMENTS
#  CNIC front/back, Father CNIC front/back,
#  Passport page1/page2, B-Form front/back, Domicile
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def identity_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = IdentityDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Identity documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 2 — MATRIC DOCUMENTS (Class 9 & 10)
#  Degree front/back, Result card front/back
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def matric_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MatricDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Matric documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 3 — INTER DOCUMENTS (Class 11 & 12)
#  Degree front/back, Result card front/back
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def inter_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InterDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Inter documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 4 — BS DOCUMENTS
#  Degree front/back, Transcript front/back
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def bs_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BSDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "BS documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 5 — MS DOCUMENTS
#  Degree front/back, Transcript front/back
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def ms_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MSDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "MS documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 6 — PROFESSIONAL DOCUMENTS
#  CV, IELTS/PTE
# ════════════════════════════════════════════════════════════════════
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def professional_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfessionalDocumentSerializer(
        doc, data=request.data, partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Professional documents updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 7 — EXPERIENCE LETTERS (multiple)
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_experience_letter(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['student'] = student.id

    serializer = ExperienceLetterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Experience letter uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 8 — REFERENCE LETTERS (multiple)
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_reference_letter(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['student'] = student.id

    serializer = ReferenceLetterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Reference letter uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 9 — OTHER DOCUMENTS (multiple)
# ════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_other_document(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['student'] = student.id

    serializer = OtherDocumentSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response({
            "status": "success",
            "message": "Document uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════════
#  API 10 — GET ALL DOCUMENTS of a student
# ════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get or create main document record
    doc, _ = StudentDocument.objects.get_or_create(student=student)

    # Get multiple documents
    experience_letters = ExperienceLetter.objects.filter(student=student)
    reference_letters  = ReferenceLetter.objects.filter(student=student)
    other_documents    = OtherDocument.objects.filter(student=student)

    return Response({
        "status": "success",
        "student": student.name,
        "documents": {
            "identity":     IdentityDocumentSerializer(doc, context={'request': request}).data,
            "matric":       MatricDocumentSerializer(doc, context={'request': request}).data,
            "inter":        InterDocumentSerializer(doc, context={'request': request}).data,
            "bs":           BSDocumentSerializer(doc, context={'request': request}).data,
            "ms":           MSDocumentSerializer(doc, context={'request': request}).data,
            "professional": ProfessionalDocumentSerializer(doc, context={'request': request}).data,
            "experience_letters": ExperienceLetterSerializer(experience_letters, many=True, context={'request': request}).data,
            "reference_letters":  ReferenceLetterSerializer(reference_letters, many=True, context={'request': request}).data,
            "other_documents":    OtherDocumentSerializer(other_documents, many=True, context={'request': request}).data,
        }
    })
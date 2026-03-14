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


# ════════════════════════════════════════════════════════════════════
#  NEW — DELETE A SINGLE GROUPED FIELD (set to null in DB + Cloudinary)
#  DELETE /documents/{student_id}/field/{field_name}/delete/
# ════════════════════════════════════════════════════════════════════

# All valid deletable file fields per group
VALID_FILE_FIELDS = {
    'identity': [
        'cnic_front', 'cnic_back', 'father_cnic_front', 'father_cnic_back',
        'passport_page1', 'passport_page2', 'b_form_front', 'b_form_back', 'domicile',
    ],
    'matric': [
        'matric_degree_front', 'matric_degree_back',
        'matric_result_card_front', 'matric_result_card_back',
    ],
    'inter': [
        'inter_degree_front', 'inter_degree_back',
        'inter_result_card_front', 'inter_result_card_back',
    ],
    'bs': ['bs_degree_front', 'bs_degree_back', 'bs_transcript_front', 'bs_transcript_back'],
    'ms': ['ms_degree_front', 'ms_degree_back', 'ms_transcript_front', 'ms_transcript_back'],
    'professional': ['cv', 'ielts_pte'],
}

ALL_VALID_FIELDS = [f for fields in VALID_FILE_FIELDS.values() for f in fields]


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_grouped_document_field(request, student_id, field_name):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    if field_name not in ALL_VALID_FIELDS:
        return Response({"error": f"Invalid field: {field_name}"}, status=status.HTTP_400_BAD_REQUEST)

    student, doc = get_or_create_document_record(student_id)
    if not student:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    file_field = getattr(doc, field_name, None)
    if not file_field:
        return Response({"error": "No file uploaded for this field."}, status=status.HTTP_404_NOT_FOUND)

    # Delete from Cloudinary (the storage backend handles this)
    file_field.delete(save=False)

    # Set field to null and save
    setattr(doc, field_name, None)
    doc.save(update_fields=[field_name])

    return Response({
        "status": "success",
        "message": f"{field_name} deleted successfully",
    }, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════════════
#  NEW — DELETE EXPERIENCE LETTER
#  DELETE /documents/experience-letter/{record_id}/delete/
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_experience_letter(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        letter = ExperienceLetter.objects.get(id=record_id)
    except ExperienceLetter.DoesNotExist:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)

    letter.file.delete(save=False)  # Delete from Cloudinary
    letter.delete()

    return Response({"status": "success", "message": "Experience letter deleted."}, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════════════
#  NEW — DELETE REFERENCE LETTER
#  DELETE /documents/reference-letter/{record_id}/delete/
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_reference_letter(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        letter = ReferenceLetter.objects.get(id=record_id)
    except ReferenceLetter.DoesNotExist:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)

    letter.file.delete(save=False)
    letter.delete()

    return Response({"status": "success", "message": "Reference letter deleted."}, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════════════
#  NEW — DELETE OTHER DOCUMENT
#  DELETE /documents/other/{record_id}/delete/
# ════════════════════════════════════════════════════════════════════
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_other_document(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    try:
        doc = OtherDocument.objects.get(id=record_id)
    except OtherDocument.DoesNotExist:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)

    doc.file.delete(save=False)
    doc.delete()

    return Response({"status": "success", "message": "Document deleted."}, status=status.HTTP_200_OK)
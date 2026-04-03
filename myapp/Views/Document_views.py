# myapp/Views/Document_views.py  —  FULLY ASYNC (100% sync_to_async safe)
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async

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


def has_access(user):
    return user.role in [User.Role.ADMIN, User.Role.CONSULTANT]


# ── Shared grouped doc upload handler ────────────────────────────────
async def _handle_doc_upload(request, student_id, SerializerClass, success_msg):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _process():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, "not_found"
        doc, _ = StudentDocument.objects.get_or_create(student=student)
        serializer = SerializerClass(doc, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(uploaded_by=request.user)
        return serializer.data, None   # .data safe — inside sync context

    result, err = await sync_to_async(_process)()
    if err == "not_found":
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    if err == "invalid":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": "success", "message": success_msg, "data": result},
                    status=status.HTTP_200_OK)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def identity_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, IdentityDocumentSerializer,
                                    "Identity documents updated successfully")

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def matric_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, MatricDocumentSerializer,
                                    "Matric documents updated successfully")

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def inter_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, InterDocumentSerializer,
                                    "Inter documents updated successfully")

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def bs_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, BSDocumentSerializer,
                                    "BS documents updated successfully")

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def ms_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, MSDocumentSerializer,
                                    "MS documents updated successfully")

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def professional_documents(request, student_id):
    return await _handle_doc_upload(request, student_id, ProfessionalDocumentSerializer,
                                    "Professional documents updated successfully")


# ── EXPERIENCE LETTERS ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_experience_letter(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _upload():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, "not_found"
        data = request.data.copy()
        data['student'] = student.id
        serializer = ExperienceLetterSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(uploaded_by=request.user)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_upload)()
    if err == "not_found":
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    if err == "invalid":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": "success", "message": "Experience letter uploaded successfully",
                     "data": result}, status=status.HTTP_201_CREATED)


# ── REFERENCE LETTERS ─────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_reference_letter(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _upload():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, "not_found"
        data = request.data.copy()
        data['student'] = student.id
        serializer = ReferenceLetterSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(uploaded_by=request.user)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_upload)()
    if err == "not_found":
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    if err == "invalid":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": "success", "message": "Reference letter uploaded successfully",
                     "data": result}, status=status.HTTP_201_CREATED)


# ── OTHER DOCUMENTS ───────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_other_document(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _upload():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, "not_found"
        data = request.data.copy()
        data['student'] = student.id
        serializer = OtherDocumentSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(uploaded_by=request.user)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_upload)()
    if err == "not_found":
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    if err == "invalid":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": "success", "message": "Document uploaded successfully",
                     "data": result}, status=status.HTTP_201_CREATED)


# ── GET ALL DOCUMENTS ─────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_student_documents(request, student_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _fetch():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return None, None
        doc, _  = StudentDocument.objects.get_or_create(student=student)
        exp_let = list(ExperienceLetter.objects.filter(student=student))
        ref_let = list(ReferenceLetter.objects.filter(student=student))
        oth_doc = list(OtherDocument.objects.filter(student=student))
        ctx = {'request': request}
        # All .data accesses are safe here — inside sync context
        documents = {
            "identity":           IdentityDocumentSerializer(doc, context=ctx).data,
            "matric":             MatricDocumentSerializer(doc, context=ctx).data,
            "inter":              InterDocumentSerializer(doc, context=ctx).data,
            "bs":                 BSDocumentSerializer(doc, context=ctx).data,
            "ms":                 MSDocumentSerializer(doc, context=ctx).data,
            "professional":       ProfessionalDocumentSerializer(doc, context=ctx).data,
            "experience_letters": ExperienceLetterSerializer(exp_let, many=True, context=ctx).data,
            "reference_letters":  ReferenceLetterSerializer(ref_let, many=True, context=ctx).data,
            "other_documents":    OtherDocumentSerializer(oth_doc, many=True, context=ctx).data,
        }
        return student.name, documents

    result = await sync_to_async(_fetch)()
    if result[0] is None:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    student_name, documents = result
    return Response({"status": "success", "student": student_name, "documents": documents})


# ── VALID DELETABLE FIELDS ────────────────────────────────────────────
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
async def delete_grouped_document_field(request, student_id, field_name):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
    if field_name not in ALL_VALID_FIELDS:
        return Response({"error": f"Invalid field: {field_name}"}, status=status.HTTP_400_BAD_REQUEST)

    def _delete():
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return "not_found"
        doc, _ = StudentDocument.objects.get_or_create(student=student)
        file_field = getattr(doc, field_name, None)
        if not file_field:
            return "no_file"
        file_field.delete(save=False)
        setattr(doc, field_name, None)
        doc.save(update_fields=[field_name])
        return "ok"

    result = await sync_to_async(_delete)()
    if result == "not_found":
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    if result == "no_file":
        return Response({"error": "No file uploaded for this field."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"status": "success", "message": f"{field_name} deleted successfully"},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_experience_letter(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _delete():
        try:
            letter = ExperienceLetter.objects.get(id=record_id)
        except ExperienceLetter.DoesNotExist:
            return False
        letter.file.delete(save=False)
        letter.delete()
        return True

    found = await sync_to_async(_delete)()
    if not found:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"status": "success", "message": "Experience letter deleted."}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_reference_letter(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _delete():
        try:
            letter = ReferenceLetter.objects.get(id=record_id)
        except ReferenceLetter.DoesNotExist:
            return False
        letter.file.delete(save=False)
        letter.delete()
        return True

    found = await sync_to_async(_delete)()
    if not found:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"status": "success", "message": "Reference letter deleted."}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def delete_other_document(request, record_id):
    if not has_access(request.user):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def _delete():
        try:
            doc = OtherDocument.objects.get(id=record_id)
        except OtherDocument.DoesNotExist:
            return False
        doc.file.delete(save=False)
        doc.delete()
        return True

    found = await sync_to_async(_delete)()
    if not found:
        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"status": "success", "message": "Document deleted."}, status=status.HTTP_200_OK)

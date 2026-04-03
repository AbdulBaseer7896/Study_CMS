# myapp/Views/Student_views.py  —  FULLY ASYNC (100% sync_to_async safe)
"""
Student portal views — all DB + serializer access inside sync_to_async wrappers.
"""
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async

from myapp.Models.Auth_models import User
from myapp.Models.Application_models import Application
from myapp.Models.Document_models import (
    StudentDocument, ExperienceLetter, ReferenceLetter, OtherDocument
)
from myapp.serializers.Application_serializers import ApplicationDetailSerializer
from myapp.serializers.Document_serializers import (
    IdentityDocumentSerializer, MatricDocumentSerializer, InterDocumentSerializer,
    BSDocumentSerializer, MSDocumentSerializer, ProfessionalDocumentSerializer,
    ExperienceLetterSerializer, ReferenceLetterSerializer, OtherDocumentSerializer,
)


def _is_student(user):
    return user.role == User.Role.STUDENT


# ── MY APPLICATIONS (read-only) ───────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def student_my_applications(request):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _fetch():
        qs = Application.objects.filter(student=request.user).order_by('-created_at')
        return ApplicationDetailSerializer(qs, many=True, context={'request': request}).data

    data = await sync_to_async(_fetch)()
    return Response({"status": "success", "applications": data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def student_get_application(request, application_id):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _fetch():
        try:
            app = Application.objects.get(id=application_id, student=request.user)
        except Application.DoesNotExist:
            return None
        return ApplicationDetailSerializer(app, context={'request': request}).data

    data = await sync_to_async(_fetch)()
    if data is None:
        return Response({"error": "Application not found."}, status=404)
    return Response({"status": "success", "application": data})


# ── MY DOCUMENTS ──────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def student_my_documents(request):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _fetch():
        doc, _ = StudentDocument.objects.get_or_create(student=request.user)
        ctx     = {'request': request}
        exp_let = list(ExperienceLetter.objects.filter(student=request.user))
        ref_let = list(ReferenceLetter.objects.filter(student=request.user))
        oth_doc = list(OtherDocument.objects.filter(student=request.user))

        def _with_edit(serializer_data, obj):
            d = dict(serializer_data)
            d['can_edit'] = obj.student_can_edit()
            return d

        # All .data accesses are safe — inside sync context
        return {
            "identity":           IdentityDocumentSerializer(doc, context=ctx).data,
            "matric":             MatricDocumentSerializer(doc, context=ctx).data,
            "inter":              InterDocumentSerializer(doc, context=ctx).data,
            "bs":                 BSDocumentSerializer(doc, context=ctx).data,
            "ms":                 MSDocumentSerializer(doc, context=ctx).data,
            "professional":       ProfessionalDocumentSerializer(doc, context=ctx).data,
            "experience_letters": [_with_edit(ExperienceLetterSerializer(e, context=ctx).data, e) for e in exp_let],
            "reference_letters":  [_with_edit(ReferenceLetterSerializer(r, context=ctx).data, r) for r in ref_let],
            "other_documents":    [_with_edit(OtherDocumentSerializer(o, context=ctx).data, o) for o in oth_doc],
        }

    docs = await sync_to_async(_fetch)()
    return Response({"status": "success", "documents": docs})


# ── Shared grouped doc upload for students ────────────────────────────
async def _student_upload_grouped(request, SerializerClass, field_names):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _process():
        doc, _ = StudentDocument.objects.get_or_create(student=request.user)
        # Check 15-min rule for each field being uploaded
        for field in field_names:
            if field in request.FILES:
                existing = getattr(doc, field, None)
                has_file = bool(existing and getattr(existing, 'name', None))
                if has_file and not doc.student_can_edit_field(field):
                    return None, f"'{field}' was uploaded more than 15 minutes ago. You cannot replace it."
        serializer = SerializerClass(doc, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        saved = serializer.save(uploaded_by=request.user)
        # Stamp upload times
        for field in field_names:
            if field in request.FILES:
                saved.record_upload_time(field)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_process)()
    if err == "invalid":
        return Response(result, status=400)
    if err:
        return Response({"error": err}, status=status.HTTP_403_FORBIDDEN)
    return Response({"status": "success", "data": result})


IDENTITY_FIELDS     = ['cnic_front','cnic_back','father_cnic_front','father_cnic_back',
                        'passport_page1','passport_page2','b_form_front','b_form_back','domicile']
MATRIC_FIELDS       = ['matric_degree_front','matric_degree_back','matric_result_card_front','matric_result_card_back']
INTER_FIELDS        = ['inter_degree_front','inter_degree_back','inter_result_card_front','inter_result_card_back']
BS_FIELDS           = ['bs_degree_front','bs_degree_back','bs_transcript_front','bs_transcript_back']
MS_FIELDS           = ['ms_degree_front','ms_degree_back','ms_transcript_front','ms_transcript_back']
PROFESSIONAL_FIELDS = ['cv','ielts_pte']


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_identity_documents(request):
    return await _student_upload_grouped(request, IdentityDocumentSerializer, IDENTITY_FIELDS)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_matric_documents(request):
    return await _student_upload_grouped(request, MatricDocumentSerializer, MATRIC_FIELDS)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_inter_documents(request):
    return await _student_upload_grouped(request, InterDocumentSerializer, INTER_FIELDS)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_bs_documents(request):
    return await _student_upload_grouped(request, BSDocumentSerializer, BS_FIELDS)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_ms_documents(request):
    return await _student_upload_grouped(request, MSDocumentSerializer, MS_FIELDS)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
async def student_professional_documents(request):
    return await _student_upload_grouped(request, ProfessionalDocumentSerializer, PROFESSIONAL_FIELDS)


# ── Multi-entry uploads ───────────────────────────────────────────────
async def _student_multi_upload(request, SerializerClass):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _upload():
        data = request.data.copy()
        data['student'] = request.user.id
        serializer = SerializerClass(data=data, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        serializer.save(uploaded_by=request.user)
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_upload)()
    if err == "invalid":
        return Response(result, status=400)
    return Response({"status": "success", "data": result}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def student_upload_experience_letter(request):
    return await _student_multi_upload(request, ExperienceLetterSerializer)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def student_upload_reference_letter(request):
    return await _student_multi_upload(request, ReferenceLetterSerializer)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def student_upload_other_document(request):
    return await _student_multi_upload(request, OtherDocumentSerializer)


# ── Multi-entry deletes (within 15 min) ──────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def student_delete_experience_letter(request, record_id):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _delete():
        try:
            letter = ExperienceLetter.objects.get(id=record_id, student=request.user)
        except ExperienceLetter.DoesNotExist:
            return "not_found"
        if not letter.student_can_edit():
            return "expired"
        letter.file.delete(save=False)
        letter.delete()
        return "ok"

    result = await sync_to_async(_delete)()
    if result == "not_found":
        return Response({"error": "Not found."}, status=404)
    if result == "expired":
        return Response({"error": "15-minute edit window has expired."}, status=403)
    return Response({"status": "success", "message": "Deleted."})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def student_delete_reference_letter(request, record_id):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _delete():
        try:
            letter = ReferenceLetter.objects.get(id=record_id, student=request.user)
        except ReferenceLetter.DoesNotExist:
            return "not_found"
        if not letter.student_can_edit():
            return "expired"
        letter.file.delete(save=False)
        letter.delete()
        return "ok"

    result = await sync_to_async(_delete)()
    if result == "not_found":
        return Response({"error": "Not found."}, status=404)
    if result == "expired":
        return Response({"error": "15-minute edit window has expired."}, status=403)
    return Response({"status": "success", "message": "Deleted."})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def student_delete_other_document(request, record_id):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)

    def _delete():
        try:
            doc = OtherDocument.objects.get(id=record_id, student=request.user)
        except OtherDocument.DoesNotExist:
            return "not_found"
        if not doc.student_can_edit():
            return "expired"
        doc.file.delete(save=False)
        doc.delete()
        return "ok"

    result = await sync_to_async(_delete)()
    if result == "not_found":
        return Response({"error": "Not found."}, status=404)
    if result == "expired":
        return Response({"error": "15-minute edit window has expired."}, status=403)
    return Response({"status": "success", "message": "Deleted."})


# ── Delete grouped field (within 15 min) ─────────────────────────────
ALL_VALID_FIELDS = (IDENTITY_FIELDS + MATRIC_FIELDS + INTER_FIELDS +
                    BS_FIELDS + MS_FIELDS + PROFESSIONAL_FIELDS)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def student_delete_grouped_field(request, field_name):
    if not _is_student(request.user):
        return Response({"error": "Permission denied."}, status=403)
    if field_name not in ALL_VALID_FIELDS:
        return Response({"error": f"Invalid field: {field_name}"}, status=400)

    def _delete():
        doc, _ = StudentDocument.objects.get_or_create(student=request.user)
        if not doc.student_can_edit_field(field_name):
            return "expired"
        file_field = getattr(doc, field_name, None)
        if not (file_field and getattr(file_field, 'name', None)):
            return "no_file"
        file_field.delete(save=False)
        setattr(doc, field_name, None)
        doc.field_upload_times.pop(field_name, None)
        doc.save(update_fields=[field_name, 'field_upload_times'])
        return "ok"

    result = await sync_to_async(_delete)()
    if result == "expired":
        return Response({"error": "15-minute edit window has expired."}, status=403)
    if result == "no_file":
        return Response({"error": "No file uploaded for this field."}, status=404)
    return Response({"status": "success", "message": f"{field_name} deleted."})

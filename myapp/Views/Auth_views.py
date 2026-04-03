# myapp/Views/Auth_views.py  —  FULLY ASYNC (100% sync_to_async safe)
"""
Rule: EVERY database access and EVERY serializer.data access must be inside
      a sync_to_async() wrapper. No ORM or serializer calls at the async level.
"""
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from asgiref.sync import sync_to_async

from myapp.Models.Auth_models import User
from myapp.serializers.User_serializers import (
    RegisterSerializer, UserSerializer, LoginSerializer
)


def _is_admin(user):
    return user.role == User.Role.ADMIN


async def homepage(request):
    return JsonResponse({"status": "success", "message": "StudyCMS API"})


# ── LOGIN ─────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
async def admin_login(request):
    def _login():
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return None, serializer.errors
        user = serializer.validated_data["user"]
        return user, None

    user, errors = await sync_to_async(_login)()
    if errors:
        return Response(errors, status=400)

    refresh = await sync_to_async(RefreshToken.for_user)(user)
    return Response({
        "status": "success",
        "access_token":  str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    })


# ── FORGOT PASSWORD: Request OTP ──────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
async def forgot_password_request(request):
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({"error": "Email is required."}, status=400)

    def _get_user():
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    user = await sync_to_async(_get_user)()
    if not user:
        return Response({"status": "success", "message": "If this email is registered, an OTP has been sent."})

    from myapp.Models.OTP_models import PasswordResetOTP
    otp_obj = await sync_to_async(PasswordResetOTP.generate_for_user)(user)

    from myapp.Utils.email_tasks import send_forgot_password_otp_task
    await sync_to_async(send_forgot_password_otp_task.delay)(user.id, otp_obj.otp)

    return Response({"status": "success", "message": "OTP sent to your email. Expires in 40 seconds."})


# ── FORGOT PASSWORD: Verify OTP & Reset ──────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
async def forgot_password_verify(request):
    email        = request.data.get('email', '').strip().lower()
    otp_code     = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not all([email, otp_code, new_password]):
        return Response({"error": "email, otp, and new_password are required."}, status=400)
    if len(new_password) < 6:
        return Response({"error": "Password must be at least 6 characters."}, status=400)

    def _verify():
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None, "invalid_email"
        from myapp.Models.OTP_models import PasswordResetOTP
        try:
            otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp_code).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return None, "invalid_otp"
        if not otp_obj.is_valid():
            return None, "expired_otp"
        otp_obj.is_used = True
        otp_obj.save()
        user.set_password(new_password)
        user.save()
        return user, None

    user, err = await sync_to_async(_verify)()
    if err == "invalid_email":
        return Response({"error": "Invalid email."}, status=400)
    if err == "invalid_otp":
        return Response({"error": "Invalid OTP."}, status=400)
    if err == "expired_otp":
        return Response({"error": "OTP has expired. Please request a new one."}, status=400)

    return Response({"status": "success", "message": "Password reset successfully. You can now log in."})


# ── CREATE USER ───────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def admin_create_user(request):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    def _create():
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return None, serializer.errors, None
        user = serializer.save()
        return user, None, serializer.data   # .data safe

    user, errors, user_data = await sync_to_async(_create)()
    if errors:
        return Response(errors, status=400)

    from myapp.Utils.email_tasks import send_welcome_email_task, send_student_welcome_task
    if user.role == User.Role.STUDENT:
        await sync_to_async(send_student_welcome_task.delay)(user.id)
    else:
        await sync_to_async(send_welcome_email_task.delay)(user.id)

    return Response({
        "status": "success",
        "message": "User created successfully",
        "user": user_data,
    }, status=201)


# ── DELETE USER ───────────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
async def admin_delete_user(request, user_id):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    def _delete():
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, "not_found"
        if user.id == request.user.id:
            return None, "self_delete"
        name = user.name
        user.delete()
        return name, None

    name, err = await sync_to_async(_delete)()
    if err == "not_found":
        return Response({"error": "User not found"}, status=404)
    if err == "self_delete":
        return Response({"error": "Cannot delete your own account"}, status=400)
    return Response({"status": "success", "message": f"User '{name}' deleted successfully"})


# ── UPDATE USER ───────────────────────────────────────────────────────
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
async def admin_update_user(request, user_id):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    def _update():
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, "not_found"
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        if 'profile_picture' in request.FILES and user.profile_picture:
            try:
                from myapp.Utils.storage_utils import delete_image
                delete_image(user.profile_picture.name)
            except Exception:
                pass
        serializer.save()
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_update)()
    if err == "not_found":
        return Response({"error": "User not found"}, status=404)
    if err == "invalid":
        return Response(result, status=400)
    return Response({"status": "success", "message": "User updated successfully", "user": result})


# ── GET ALL USERS — paginated ─────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def admin_get_all_users(request):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    role      = request.query_params.get('role')
    search    = request.query_params.get('search', '').strip()
    page_size = int(request.query_params.get('page_size', 10))
    page_size = min(max(page_size, 1), 100)

    if role and role not in ['admin', 'student', 'consultant']:
        return Response({"error": "Invalid role."}, status=400)

    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100

    def _fetch():
        from django.db.models import Q
        qs = User.objects.all().order_by('id')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        total      = qs.count()
        paginated  = paginator.paginate_queryset(qs, request)
        serializer = UserSerializer(paginated, many=True, context={'request': request})
        return total, serializer.data   # .data safe

    total, data = await sync_to_async(_fetch)()
    return paginator.get_paginated_response({
        "status": "success",
        "total_users": total,
        "users": data,
    })


# ── SELF UPDATE ───────────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
async def me_update(request):
    def _update():
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return serializer.errors, "invalid"
        if 'profile_picture' in request.FILES and user.profile_picture:
            try:
                from myapp.Utils.storage_utils import delete_image
                delete_image(user.profile_picture.name)
            except Exception:
                pass
        serializer.save()
        return serializer.data, None   # .data safe

    result, err = await sync_to_async(_update)()
    if err == "invalid":
        return Response(result, status=400)
    return Response({"status": "success", "message": "Profile updated successfully", "user": result})

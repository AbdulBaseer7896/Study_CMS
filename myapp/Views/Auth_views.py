# myapp/Views/Auth_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

from myapp.Models.Auth_models import User
from myapp.serializers.User_serializers import (
    RegisterSerializer, UserSerializer, LoginSerializer
)


def _is_admin(user):
    return user.role == User.Role.ADMIN


def homepage(request):
    return JsonResponse({"status": "success", "message": "StudyCMS API"})


# ── LOGIN ─────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "access_token":  str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        })
    return Response(serializer.errors, status=400)


# ── FORGOT PASSWORD: Request OTP ──────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"status": "success", "message": "If this email is registered, an OTP has been sent."})

    from myapp.Models.OTP_models import PasswordResetOTP
    from myapp.Utils.email_tasks import send_forgot_password_otp_task

    otp_obj = PasswordResetOTP.generate_for_user(user)
    send_forgot_password_otp_task.delay(user.id, otp_obj.otp)

    return Response({"status": "success", "message": "OTP sent to your email. Expires in 40 seconds."})


# ── FORGOT PASSWORD: Verify OTP & Reset ──────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verify(request):
    email        = request.data.get('email', '').strip().lower()
    otp_code     = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not all([email, otp_code, new_password]):
        return Response({"error": "email, otp, and new_password are required."}, status=400)
    if len(new_password) < 6:
        return Response({"error": "Password must be at least 6 characters."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=400)

    from myapp.Models.OTP_models import PasswordResetOTP
    try:
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp_code).latest('created_at')
    except PasswordResetOTP.DoesNotExist:
        return Response({"error": "Invalid OTP."}, status=400)

    if not otp_obj.is_valid():
        return Response({"error": "OTP has expired. Please request a new one."}, status=400)

    otp_obj.is_used = True
    otp_obj.save()
    user.set_password(new_password)
    user.save()

    return Response({"status": "success", "message": "Password reset successfully. You can now log in."})


# ── CREATE USER ───────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    serializer = RegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        from myapp.Utils.email_tasks import send_welcome_email_task, send_student_welcome_task
        if user.role == User.Role.STUDENT:
            send_student_welcome_task.delay(user.id)
        else:
            send_welcome_email_task.delay(user.id)

        return Response({"status": "success", "message": "User created successfully", "user": serializer.data}, status=201)
    return Response(serializer.errors, status=400)


# ── DELETE USER ───────────────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    if user.id == request.user.id:
        return Response({"error": "Cannot delete your own account"}, status=400)
    name = user.name
    user.delete()
    return Response({"status": "success", "message": f"User '{name}' deleted successfully"})


# ── UPDATE USER ───────────────────────────────────────────────────────
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, user_id):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        if 'profile_picture' in request.FILES and user.profile_picture:
            try:
                from myapp.Utils.storage_utils import delete_image
                delete_image(user.profile_picture.name)
            except Exception:
                pass
        serializer.save()
        return Response({"status": "success", "message": "User updated successfully", "user": serializer.data})
    return Response(serializer.errors, status=400)


# ── GET ALL USERS ─────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_all_users(request):
    if not _is_admin(request.user):
        return Response({"error": "Permission denied"}, status=403)

    role  = request.query_params.get('role')
    users = User.objects.all().order_by('id')
    if role:
        if role not in ['admin', 'student', 'consultant']:
            return Response({"error": "Invalid role."}, status=400)
        users = users.filter(role=role)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100
    paginated  = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated, many=True, context={'request': request})
    return paginator.get_paginated_response({"status": "success", "total_users": users.count(), "users": serializer.data})


# ── SELF UPDATE ───────────────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def me_update(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        if 'profile_picture' in request.FILES and user.profile_picture:
            try:
                from myapp.Utils.storage_utils import delete_image
                delete_image(user.profile_picture.name)
            except Exception:
                pass
        serializer.save()
        return Response({"status": "success", "message": "Profile updated successfully", "user": serializer.data})
    return Response(serializer.errors, status=400)

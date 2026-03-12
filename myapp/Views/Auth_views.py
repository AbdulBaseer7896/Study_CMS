from rest_framework import generics, permissions
from myapp.Models.Auth_models import User
from myapp.serializers.User_serializers import RegisterSerializer, UserSerializer
from django.http import JsonResponse

# class 

# class RegisterView(generics.CreateAPIView):
#     """POST /api/users/register/ — anyone can register"""
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [permissions.AllowAny]  # override the global IsAuthenticated

# class MeView(generics.RetrieveUpdateAPIView):
#     """GET/PUT /api/users/me/ — get or update current user's profile"""
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user  # return the logged-in user



#### Home Page View
# @login_required
def homepage(request):
    print("This is the home page")
    return JsonResponse({"staus": "success"})




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from myapp.serializers.User_serializers import LoginSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from myapp.serializers.User_serializers import LoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])   # ← add this
def admin_login(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "success",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        })

    return Response(serializer.errors, status=400)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from myapp.Models.Auth_models import User
from myapp.serializers.User_serializers import RegisterSerializer, UserSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    if request.user.role != 'admin':
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    # Only admin can delete users
    if request.user.role != 'admin':
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Prevent admin from deleting themselves
    if user.id == request.user.id:
        return Response({"error": "You cannot delete your own account"}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response({
        "status": "success",
        "message": f"User '{user.name}' deleted successfully"
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, user_id):
    # Only admin can update users
    if request.user.role != 'admin':
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # partial=True allows PATCH (update only provided fields)
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "User updated successfully",
            "user": serializer.data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_all_users(request):
    # Only admin can access
    if request.user.role != 'admin':
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Get query param ?role=student or ?role=consultant
    role = request.query_params.get('role', None)

    users = User.objects.all().order_by('id')

    # Filter by role if provided
    if role:
        valid_roles = ['admin', 'student', 'consultant']
        if role not in valid_roles:
            return Response(
                {"error": f"Invalid role. Choose from: {', '.join(valid_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        users = users.filter(role=role)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10                        # 10 users per page
    paginator.page_size_query_param = 'page_size'   # allow ?page_size=5
    paginator.max_page_size = 100

    paginated_users = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated_users, many=True)

    return paginator.get_paginated_response({
        "status": "success",
        "total_users": users.count(),
        "users": serializer.data
    })


# What you wantURLAll users (page 1)http://127.0.0.1:8000/api/v1/admin/users/Page 2
# http://127.0.0.1:8000/api/v1/admin/users/?page=2Only students
# http://127.0.0.1:8000/api/v1/admin/users/?role=studentOnly consultants
# http://127.0.0.1:8000/api/v1/admin/users/?role=consultantStudents, 5 per page
# http://127.0.0.1:8000/api/v1/admin/users/?role=student&page_size=5Students page 2
# http://127.0.0.1:8000/api/v1/admin/users/?role=student&page=2
# In Postman, add params via the Params tab — no need to type them in the URL manually:
# KEYVALUErolestudentpage1page_size5
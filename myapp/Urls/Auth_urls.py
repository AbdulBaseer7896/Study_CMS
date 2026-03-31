from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp.Views.Auth_views import (
    homepage, admin_login,
    admin_create_user, admin_delete_user, admin_update_user, admin_get_all_users,
    me_update,
    forgot_password_request, forgot_password_verify,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('home', homepage, name='home'),
    path('login/', admin_login, name='admin_login'),

    # Token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Forgot Password
    path('forgot-password/', forgot_password_request, name='forgot_password_request'),
    path('forgot-password/verify/', forgot_password_verify, name='forgot_password_verify'),

    # Admin User Management
    path('admin/users/create/', admin_create_user, name='admin_create_user'),
    path('admin/users/<int:user_id>/delete/', admin_delete_user, name='admin_delete_user'),
    path('admin/users/<int:user_id>/update/', admin_update_user, name='admin_update_user'),
    path('admin/users/', admin_get_all_users, name='admin_get_all_users'),

    # Self-update
    path('me/update/', me_update, name='me_update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

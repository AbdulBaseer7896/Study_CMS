from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp.Views.Auth_views import homepage , admin_login , admin_create_user, admin_delete_user, admin_update_user , admin_get_all_users

urlpatterns = [
    path('home', homepage , name="home"),
    path('login/', admin_login, name="admin_login"),



    # Admin User Management
    path('admin/users/create/', admin_create_user, name="admin_create_user"),
    path('admin/users/<int:user_id>/delete/', admin_delete_user, name="admin_delete_user"),
    path('admin/users/<int:user_id>/update/', admin_update_user, name="admin_update_user"),
    path('admin/users/', admin_get_all_users, name="admin_get_all_users"),

]

# Serve uploaded files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('myapp.Urls.Auth_urls')),
    path('api/v1/', include('myapp.Urls.Consultant_urls')),
    path('api/v1/', include('myapp.Urls.Document_urls')),
    path('api/v1/', include('myapp.Urls.Application_urls')),
    path('api/v1/', include('myapp.Urls.Student_urls')),
    path('api/v1/', include('myapp.Urls.Chat_urls')),
    path('api/v1/', include('myapp.Urls.Webhook_urls')),
]

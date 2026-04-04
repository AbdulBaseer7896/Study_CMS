from django.urls import path
from myapp.Views.Webhook_views import meta_webhook

urlpatterns = [
    path('webhook/meta/', meta_webhook, name='meta_webhook'),
]
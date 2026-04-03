"""
ASGI config for studyCMS — HTTP (Django) + WebSocket (Channels).

New WS URL: /ws/chat/user/   (ONE connection per user, covers all convs)
Old URL:    /ws/chat/<id>/   (kept for backward compat — routes to same consumer)
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyCMS.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path
from myapp.consumers.chat_consumer import ChatConsumer

websocket_urlpatterns = [
    # New: single socket per user
    re_path(r'^ws/chat/user/$', ChatConsumer.as_asgi()),
    # Legacy: kept so old clients don't 404 (same consumer handles it)
    re_path(r'^ws/chat/(?P<conv_id>\d+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        URLRouter(websocket_urlpatterns)
    ),
})

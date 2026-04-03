"""
ASGI config for studyCMS — HTTP (Django) + WebSocket (Channels).

WS URL:  /ws/chat/user/   (ONE connection per user, covers all convs)
Legacy:  /ws/chat/<id>/   (backward compat — routes to same consumer)

Origin validation:
  AllowedHostsOriginValidator is replaced with a custom validator that
  accepts connections from the Netlify frontend (studycms.netlify.app)
  even though the WebSocket connects directly to the DigitalOcean backend
  (157.245.100.38). The browser sends Origin: https://studycms.netlify.app
  which would be rejected by AllowedHostsOriginValidator since it only
  checks against ALLOWED_HOSTS (the backend's own domain/IP).
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyCMS.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.middleware import BaseMiddleware
from django.urls import re_path
from myapp.consumers.chat_consumer import ChatConsumer

# Allowed origins for WebSocket connections.
# Add your Netlify domain and any other frontend origins here.
WS_ALLOWED_ORIGINS = {
    'https://studycms.netlify.app',
    'http://studycms.netlify.app',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://157.245.100.38',
    'https://157.245.100.38',
}


class AllowedOriginsMiddleware(BaseMiddleware):
    """
    WebSocket origin validator.
    Rejects connections whose Origin header is not in WS_ALLOWED_ORIGINS.
    Connections with no Origin header (e.g. from curl/Postman) are allowed.
    """
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            headers = dict(scope.get('headers', []))
            origin  = headers.get(b'origin', b'').decode('utf-8', errors='replace')
            if origin and origin not in WS_ALLOWED_ORIGINS:
                # Reject with 403
                await send({'type': 'websocket.close', 'code': 4003})
                return
        await super().__call__(scope, receive, send)


websocket_urlpatterns = [
    re_path(r'^ws/chat/user/$',              ChatConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<conv_id>\d+)/$',  ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedOriginsMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})

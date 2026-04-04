import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

VERIFY_TOKEN = "studycms_meta_verify_2026"  # you choose this string


@csrf_exempt
def meta_webhook(request):

    # ── GET: Meta verification handshake ─────────────────────────
    if request.method == "GET":
        mode      = request.GET.get("hub.mode")
        token     = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print(f"✅ Webhook verified successfully!")
            return HttpResponse(challenge, status=200)
        else:
            print(f"❌ Webhook verification failed. Token: {token}")
            return HttpResponse("Forbidden", status=403)

    # ── POST: Incoming lead data ──────────────────────────────────
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            print("=" * 60)
            print("📥 META WEBHOOK DATA RECEIVED:")
            print(json.dumps(data, indent=2))
            print("=" * 60)
            logger.info(f"Meta webhook received: {data}")
        except Exception as e:
            print(f"Error parsing webhook data: {e}")

        return HttpResponse("EVENT_RECEIVED", status=200)
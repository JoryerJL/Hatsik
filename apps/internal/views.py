from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def close_expired_events(request):
    """
    Internal endpoint called by EventBridge Scheduler every 5 minutes.

    Verifies the X-Internal-Token header and closes expired events.
    """
    token = request.headers.get("X-Internal-Token", "")

    if not token or token != settings.INTERNAL_CRON_TOKEN:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    from apps.events.services import close_expired_events as do_close

    closed_count = do_close()

    return JsonResponse({"status": "ok", "closed_count": closed_count})

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
    Business logic will be implemented in Phase 3.
    """
    token = request.headers.get("X-Internal-Token", "")

    if not token or token != settings.INTERNAL_CRON_TOKEN:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # TODO(Phase 3): Implement actual event closure logic
    # UPDATE events SET status='closed' WHERE assignment_deadline_at <= NOW()
    #   AND status = 'active'

    return JsonResponse({"status": "ok", "closed_count": 0})

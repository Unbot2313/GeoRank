import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class N8nNotificationError(Exception):
    """Falló el envío de la notificación a n8n."""


def trigger_workflow(event: str, payload: dict) -> None:
    try:
        response = requests.post(
            settings.N8N_WEBHOOK_URL,
            json={'event': event, **payload},
            headers={'X-GeoRank-Token': settings.N8N_WEBHOOK_SECRET},
            timeout=settings.N8N_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise N8nNotificationError(
            f'n8n webhook failed for event {event}: {exc}'
        ) from exc
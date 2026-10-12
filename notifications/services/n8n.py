import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class N8nNotificationError(Exception):
    """Sending the notification to n8n failed."""


def trigger_workflow(event, payload, *, url=None, files=None, timeout=None):
    target_url = url or settings.N8N_WEBHOOK_URL
    headers = {'X-GeoRank-Token': settings.N8N_WEBHOOK_SECRET}
    data = {'event': event, **payload}
    timeout = timeout or settings.N8N_TIMEOUT

    try:
        if files:
            # multipart: n8n receives each file as binary data
            response = requests.post(
                target_url, data=data, files=files,
                headers=headers, timeout=timeout,
            )
        else:
            response = requests.post(
                target_url, json=data,
                headers=headers, timeout=timeout,
            )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise N8nNotificationError(
            f'n8n webhook failed for event {event}: {exc}'
        ) from exc
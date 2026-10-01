from unittest.mock import patch

import requests
from django.test import SimpleTestCase, override_settings

from notifications.services.n8n import N8nNotificationError, trigger_workflow


@override_settings(
    N8N_WEBHOOK_URL='http://n8n.test/webhook/x',
    N8N_WEBHOOK_SECRET='secret',
    N8N_TIMEOUT=5,
)
class TriggerWorkflowTests(SimpleTestCase):
    @patch('notifications.services.n8n.requests.post')
    def test_posts_payload_with_token(self, mock_post):
        trigger_workflow('analysis.ready', {'to': 'a@b.com'})
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['event'], 'analysis.ready')
        self.assertEqual(kwargs['json']['to'], 'a@b.com')
        self.assertEqual(kwargs['headers']['X-GeoRank-Token'], 'secret')

    @patch('notifications.services.n8n.requests.post',
           side_effect=requests.ConnectionError('down'))
    def test_wraps_request_errors(self, _mock_post):
        with self.assertRaises(N8nNotificationError):
            trigger_workflow('analysis.ready', {})
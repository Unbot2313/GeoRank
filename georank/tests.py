from django.test import TestCase, override_settings


class NotFoundPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_unknown_url_uses_custom_not_found_page(self):
        response = self.client.get('/this-page-does-not-exist/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Page not found', status_code=404)
        self.assertContains(response, 'Go to home', status_code=404)

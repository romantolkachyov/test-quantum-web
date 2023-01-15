from unittest.mock import Mock, patch

from django.test import TestCase


class StartViewTest(TestCase):
    @patch("quantum_web.webapp.views.cache.client.get_client")
    async def test_simple(self, get_client_mock: Mock):
        resp = await self.async_client.get("/api/start")
        self.assertEqual(resp.status_code, 200)

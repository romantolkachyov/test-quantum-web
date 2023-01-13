from django.test import TestCase


class StartViewTest(TestCase):
    async def test_simple(self):
        resp = await self.async_client.get("/api/start")
        self.assertEqual(resp.status_code, 200)

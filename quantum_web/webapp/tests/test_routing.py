from unittest import TestCase

from quantum_web.webapp.routing import websocket_urlpatterns


class SimpleRouteTest(TestCase):
    def test_routes_valid(self):
        self.assertIsInstance(websocket_urlpatterns, list)

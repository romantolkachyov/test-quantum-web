"""
ASGI config for quantum_web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quantum_web.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from quantum_web.webapp import routing as webapp  # noqa

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(webapp.websocket_urlpatterns)
})

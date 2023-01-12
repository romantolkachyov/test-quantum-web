from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/process/(?P<process_id>[\w\-]+)/$", consumers.QuantumProcessConsumer.as_asgi()),
]

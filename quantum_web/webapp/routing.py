from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/process/(?P<job_id>[\w\-]+)/$", consumers.SteamingRequestConsumer.as_asgi()),
]

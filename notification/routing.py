# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/room/<str:room_id>/', consumers.GroupConsumer.as_asgi()),
]

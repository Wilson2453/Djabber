from django.urls import path 

from . import consumers

# Urls for our websockets
websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]
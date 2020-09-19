from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
# from home.consumers import MessageConsumer, EditorConsumer
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_recommendation.settings')
django.setup()
websocket_urlpatterns = [
    # url('socket/streaming/', MessageConsumer),
    # url('socket/editor/', EditorConsumer)
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
    	URLRouter(
            websocket_urlpatterns
    	)
    )
})
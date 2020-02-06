import pytest
import asyncio

from django.test import Client
from django.contrib.auth.models import User

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from apps.chat.consumers import ChatAppConsumer
from core.models.models import ChatUser

from core.settings.routing import application

TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

@database_sync_to_async
def create_user(username='username', password='password'):
    user = User.objects.create_user(username=username, password=password)
    chatuser = ChatUser.objects.create(user=user)
    user.save()
    return chatuser

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebsocketChatApp:

    async def get_authenticated_user(self, client, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        chatuser = await create_user()
        client.force_login(chatuser.user)
        return chatuser

    async def get_authenticated_communicator(self, settings):
        client = Client()
        chatuser = await self.get_authenticated_user(client, settings)

        communicator = WebsocketCommunicator(
            application=application,
            path='ws/chat/',
            headers=[(
                b'cookie',
                f'sessionid={client.cookies["sessionid"].value}'.encode('ascii')
            )]
        )

        connected, _ = await communicator.connect()
        assert connected is True
        return (communicator, chatuser)

    async def test_simple(self, settings):
        communicator, chatuser = await self.get_authenticated_communicator(settings)
        communicator.disconnect()
        assert False

        


# @pytest.mark.asyncio
# async def test_connect(chatapp_instance):
#     chatapp, connect = await chatapp_instance()
#     assert connect

# @pytest.mark.asyncio
# async def test_consumer():
#     communicator = WebsocketCommunicator(ChatAppConsumer, 'GET', 'ws/chat/')
#     response = await communicator.get_response()
#     assert response['status'] == 200

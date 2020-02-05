import pytest

from django.test import Client
from django.contrib.auth.models import User

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from apps.chat.consumers import ChatAppConsumer
from core.models.models import ChatUser

from core.settings.routing import application

def create_user(username='username', password='password'):
    user = User.objects.create_user(username=username, password=password)
    chatuser = ChatUser.objects.create(user=user)
    user.save()
    return user

@pytest.fixture
def chatapp_instance():
    async def inner():
        communicator = WebsocketCommunicator(ChatAppConsumer, 'ws/chat/')
        connect, subprotocol = await communicator.connect()
        return (communicator, connect, subprotocol)
    return inner

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class WebsocketTestCase:

    def get_authenticated_user(self, client):
        user, chatuser = create_user()
        client.force_login(user)
        return user, chatuser

    async def get_(self):
        client = Client()
        user, chatuser = get_authenticated_user(client)

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
        await connected.disconnect()


# @pytest.mark.asyncio
# async def test_connect(chatapp_instance):
#     chatapp, connect = await chatapp_instance()
#     assert connect

# @pytest.mark.asyncio
# async def test_consumer():
#     communicator = WebsocketCommunicator(ChatAppConsumer, 'GET', 'ws/chat/')
#     response = await communicator.get_response()
#     assert response['status'] == 200

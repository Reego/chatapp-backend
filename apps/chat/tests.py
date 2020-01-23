import pytest
from channels.testing import HttpCommunicator
from apps.chat.consumers import ChatAppConsumer

@pytest.mark.asyncio
async def test_consumer():
    communicator = HttpCommunicator(ChatAppConsumer, 'GET', '/test/')
    response = await communicator.get_response()
    assert response['body'] == b'test response'
    assert response['status'] == 200

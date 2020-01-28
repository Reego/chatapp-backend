# def test_first_tes():
#     assert 'a' == 'a'

# class TestChatUser:
#     pass

# class TestGroup:
#     pass

# class TestNotifications:
#     pass

# class TestMessage:
#     pass

import pytest
from django.contrib.auth.models import User
from core.models.models import ChatUser, Group, Notifications, Message

pytestmark = pytest.mark.django_db

@pytest.mark.django_db
class TestChatUser:
    pytestmark = pytest.mark.django_db

    def create_chat_user(self):
        user = User.objects.create(username='SAMPLE_USER')
        return ChatUser.objects.create(user=user)

    def create_group(self):
        return Group.objects.create()

    def test_chat_user_profile_pairing(self): # tests chat user connection to auth user
        USERNAME = 'TEST_USER'
        user = User.objects.create(username=USERNAME)
        assert ChatUser.get_chat_user(user).user.username == USERNAME

    def test_create_group(self):
        GROUP_NAME = 'GROUP_NAME'
        data = {
            'group_name': GROUP_NAME
        }

        chat_user = self.create_chat_user()
        group = chat_user.create_group(data)

        assert chat_user.groups.filter(id=group.id).exists()
        assert group.group_name == chat_user.groups.get().group_name

    def test_delete_group(self):
        chat_user = self.create_chat_user()
        group = self.create_group()

        chat_user.groups.add(group)

        data = {
            'group_id': group.id,
        }

        chat_user.delete_group(data)

        assert not chat_user.groups.filter(id=group.id).exists()

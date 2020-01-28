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

    def add_group_to_chat_user(self, user, group, read=False):
        
        notifications = Notifications.objects.create(user=user, group=group, read=read)
        user.groups.add(group)

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

        self.add_group_to_chat_user(chat_user, group)

        chat_user.delete_group(data)

        assert not chat_user.groups.filter(id=group.id).exists()

    def test_get_group(self):

        chat_user = self.create_chat_user()
        
        group = self.create_group()
        group_id = group.id

        assert group == chat_user.get_group(group_id)

    def test_get_groups(self):

        chat_user = self.create_chat_user()

        group = self.create_group()
        group2 = self.create_group()
        group3 = self.create_group()

        self.add_group_to_chat_user(group)
        self.add_group_to_chat_user(group2)
        self.add_group_to_chat_user(group3)

        all_groups = chat_user.get_groups()
        assert group in all_groups and group2 in all_groups and group3 in all_groups

    def test_username(self):

        USERNAME = 'USERNAME'
        user = User(username=USERNAME)
        chat_user = ChatUser.objects.create(user=user)
        assert chat_user.username == user.username

    def test_get_notifications(self):

        chat_user = self.create_chat_user()
        
        groups = (self.create_group(), self.create_group())
        for group in groups:
            self.add_group_to_chat_user(chat_user, group)

        for notifications_obj in notifications_list.all():
            assert notifications_obj.group in groups
            assert notifications_obj.user == chat_user

class TestGroup:
    
    def test_send_message(self):
        pass

    def test_get_notifications(self): # is this even necessary?
        pass

    def test_add_user(self):
        pass

    def test_remove_user(self): # these two should not be class methods
        pass

    def test_change_group_name(self):
        pass

class TestNotifications:
    pass

class TestMessage:
    pass
        



import pytest
from django.contrib.auth.models import User
from core.models.models import ChatUser, Group, Notifications, Message

pytestmark = pytest.mark.django_db

@pytest.fixture
def chat_user_instance(db):
    user = User.objects.create(username='SAMPLE_USER')
    user.save()
    return user.chatuser
    #return ChatUser.objects.create(user=user)

@pytest.fixture
def group_instance(db):
    return Group.objects.create()

@pytest.fixture(name='add_group_to_chat_user')
def add_group_to_chat_user_fixture(db):
    def inner(chat_user, group, read=False):
        notifications = Notifications.objects.create(chat_user=chat_user, group=group, read=read)
        chat_user.groups.add(group)
    return inner

@pytest.fixture(name='create_chat_group')
def create_chat_group_fixture(db):
    def inner(chat_user, read=False):
        group = Group.objects.create()
        notifications = Notifications.objects.create(chat_user=chat_user, group=group, read=read)
        chat_user.groups.add(group)
        return group
    return inner

@pytest.fixture(name='create_message')
def create_message_fixture(db):
    def inner(group, message='MESSAGE', username='USERNAME'):
        return Message.objects.create(group, message, username)
    return inner

@pytest.mark.django_db
class TestChatUser:
    pytestmark = pytest.mark.django_db

    def test_chat_user_profile_pairing(self): # tests chat user connection to auth user
        USERNAME = 'USERNAME'
        user = User.objects.create(username=USERNAME)
        assert ChatUser.get_chat_user(user).user.username == USERNAME

    def test_username(self): # tests username property

        USERNAME = 'USERNAME'
        user = User.objects.create(username=USERNAME)
        chat_user = user.chatuser
        assert chat_user.username == user.username

    def test_create_group(self, chat_user_instance): # tests create_group method
        GROUP_NAME = 'GROUP_NAME'
        data = {
            'group_name': GROUP_NAME
        }
        group = chat_user_instance.create_group(data)

        assert chat_user_instance.groups.filter(id=group.id).exists()
        assert group.group_name == chat_user_instance.groups.get().group_name

    def test_delete_group(self, chat_user_instance, create_chat_group): # tests delete_group_method
        group = create_chat_group(chat_user_instance)

        data = {
            'group_id': group.id,
        }
        chat_user_instance.delete_group(data)

        assert not chat_user_instance.groups.filter(id=group.id).exists()

    def test_get_group(self, chat_user_instance, create_chat_group): # tests get_group method
        group = create_chat_group(chat_user_instance)
        group_id = group.id

        assert group == chat_user_instance.get_group(group_id)

    def test_get_groups(self, chat_user_instance, create_chat_group): # tests get_groups method

        group1 = create_chat_group(chat_user_instance)
        group2 = create_chat_group(chat_user_instance)
        group3 = create_chat_group(chat_user_instance)

        all_groups = chat_user_instance.get_groups()
        assert group1 in all_groups and group2 in all_groups and group3 in all_groups

    def test_get_notifications_obj(self, chat_user_instance, create_chat_group): # tests get_notifications_obj method

        groups = (
            create_chat_group(chat_user_instance),
            create_chat_group(chat_user_instance)
        )

        for group in groups:
            notifications = chat_user_instance.get_notifications_obj(group.id)
            assert notifications.group == group
            assert notifications.chat_user == chat_user_instance

@pytest.mark.django_db
class TestGroup:
    pytestmark = pytest.mark.django_db

    def test_default_time(self, group_instance):

        assert group_instance.last_message_time is None

    def test_send_message(self, chat_user_instance, create_chat_group, create_message):
        CONTENT = 'CONTENT'
        USERNAME = 'USERNAME'

        group = create_chat_group(chat_user_instance)
        # message = create_message(group)
        group.send_message(CONTENT, USERNAME)

        assert Message.objects.filter(group__id=group.id, username='').exists()
        assert Message.objects.filter(group__id=group.id, username=USERNAME).exists()

    def test_add_user(self, chat_user_instance, group_instance):
        group_instance.add_user(chat_user_instance.username)
        assert group_instance.chatuser_set.filter(id=chat_user_instance.id).exists()

    def test_remove_user(self, chat_user_instance, create_chat_group): # these two should not be class methods
        group = create_chat_group(chat_user_instance)
        group.remove_user(chat_user_instance.username)
        assert not group.chatuser_set.filter(id=chat_user_instance.user.id).exists()

    def test_change_group_name(self, group_instance):
        GROUP_NAME = 'GROUP_NAME'
        GROUP_NAME_NEW = 'NAME'
        group_instance.group_name = GROUP_NAME
        group_instance.change_name(GROUP_NAME_NEW)
        assert group_instance.group_name == GROUP_NAME_NEW



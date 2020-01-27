from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from bleach import clean
from timezone import timezone

class ChatUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    groups = models.ManyToManyField(Group)

    def create_group(self, data):
        group_name = data['group_name']
        group = Group.objects.create(group_name=group_name)
        group.save()
        notifications = Notifications.objects.create(user=self, group=group)
        notifications.save()
        self.groups.collection.add(group)

    def delete_group(self, data):
        group_name = data['group_name']
        group_id = data['group_id']

        group = Group.objects.get(id=group_id)
        self.groups.collection.remove(group)
        if len(group.user_set.all()) == 0:
            group.notifications.delete()
            group.delete()

    def get_group(self, group, return_messages = False):

        group_obj = {
            'group_id': group.id,
            'group_name': group.name,
            'messages': group.message,
            'read': Notification.objects.get(user=self, group=group).read
        }

        return group_obj

    def get_groups(self):

        return [get_group(g, False) for g in self.groups]

    @property
    def username(self):
        return self.user.username

def create_chat_user(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)

post_save.connect(create_chat_user, sender=User)


class Group(models.Model):
    group_name = models.CharField(max_length=150)
    last_message_time = models.DateField(null=True)

    def send_message(self, content, username):
        now = timezone.now()
        if now > :
            date_message = Message.objects.create(group=self, content=now)
            date_message.save()
        message = Message.objects.create(group=self, content=clean(content), username=username)
        self.last_message_time = now
        message.save()

    @classmethod
    def add_user(cls, group_id, username):
        user = ChatUser.objects.get(username=username).groups.add(group)
        if user:
            group = Group.objects.get(id=group_id)
            user.groups.collection.add(group)

    @classmethod
    def remove_user(cls, group_id, username):
        user = ChatUser.objects.get(username=username)
        if user:
            user.groups.collection.remove(id=group_id)

    @classmethod
    def change_name(cls, group_id, new_name):
        cls.objects.get(id=group_id).group_name = new_name


class Notifications(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    read = models.BooleanField(default=True)

class Message(models.Model):
    group = models.ForeignKey(group, on_delete=models.CASCADE)
    content = models.TextField()
    username = models.CharField(max_length=150)

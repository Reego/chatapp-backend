from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from bleach import clean
from datetime import datetime

class ChatUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField('Group')

    @classmethod
    def get_chat_user(cls, user):
        try:
            return ChatUser.objects.get(user=user)
        except ChatUser.DoesNotExist:
            return None

    def create_group(self, data):
        group_name = data['group_name']
        group = Group.objects.create(group_name=group_name)
        group.save()

        notifications = Notifications.objects.create(user=self, group=group)
        notifications.save()

        self.groups.add(group)

        return group

    def delete_group(self, data):
        group_id = data['group_id']

        group = Group.objects.get(id=group_id)
        self.groups.remove(group)
        if len(group.chatuser_set.all()) == 0:
            group.get_notifications().delete()
            group.delete()

    def get_group(self, group_id):
        return self.groups.get(id=group_id)

    def has_read(self, group_id):
        return Notification.objects.get(user=self, group=group).read

    def get_groups(self):

        return [get_group(g, False) for g in self.groups]

    @property
    def username(self):
        return self.user.username

    def get_notifications(self):
        return Notifications.objects.get(user__id=self.id)

def create_chat_user(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)

post_save.connect(create_chat_user, sender=User)

class Group(models.Model):
    group_name = models.CharField(max_length=150)
    last_message_time = models.DateTimeField(null=True)

    def send_message(self, content, username):
        now = datetime.utcnow()
        time_difference = now - self.last_message_time
        if difference.days > 0 :
            date_message = Message.objects.create(group=self, content=now)
            date_message.save()
        message = Message.objects.create(group=self, content=clean(content), username=username)
        self.last_message_time = now
        message.save()

    def get_notifications(self):
        return Notifications.objects.get(group__id=self.id)

    @classmethod
    def add_user(cls, group_id, username):
        user = ChatUser.objects.get(username=username).groups.add(group)
        if user:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)

    @classmethod
    def remove_user(cls, group_id, username):
        user = ChatUser.objects.get(username=username)
        if user:
            user.groups.remove(id=group_id)

    @classmethod
    def change_name(cls, group_id, new_name):
        cls.objects.get(id=group_id).group_name = new_name


class Notifications(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    read = models.BooleanField(default=True)

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField()
    username = models.CharField(max_length=150)

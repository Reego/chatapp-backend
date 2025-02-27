from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from bleach import clean
from datetime import datetime

class ChatUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField('Group')

    # user related

    @property
    def username(self):
        return self.user.username

    @classmethod
    def get_chat_user(cls, user):
        try:
            return ChatUser.objects.get(user=user)
        except ChatUser.DoesNotExist:
            return None

    # group related

    def create_group(self, group_name):
        group = Group.objects.create(group_name=group_name)
        group.save()

        notifications = Notifications.objects.create(chat_user=self, group=group)
        notifications.save()

        self.groups.add(group)

        return group

    def delete_group(self, group_id):
        group = Group.objects.get(id=group_id)
        self.groups.remove(group)
        if len(group.chatuser_set.all()) == 0:
            self.get_notifications_obj(group.id).delete()
            group.delete()

    def get_group(self, group_id):
        return self.groups.get(id=group_id)

    def get_groups(self):

        return [self.get_group(g.id) for g in self.groups.all()]

    # notifications related

    def has_read(self, group_id):
        return Notifications.objects.filter(chat_user__id=self.id, group__id=group_id).get().read

    def get_notifications_obj(self, group_id):
        return Notifications.objects.filter(chat_user__id=self.id, group__id=group_id).get()

def create_chat_user(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)

post_save.connect(create_chat_user, sender=User)

class Group(models.Model):
    group_name = models.CharField(max_length=150)
    last_message_time = models.DateTimeField(null=True)

    def send_message(self, content, username=''):
        if(username != ''):
            now = datetime.utcnow()
            if self.last_message_time is None or (now - self.last_message_time).days > 100000:
                date_message = Message.objects.create(group=self, content=now)
                date_message.save()
            self.last_message_time = now
        message = Message.objects.create(group=self, content=clean(content), username=username)
        message.save()

    def add_user(self, username):
        chat_user = ChatUser.get_chat_user(User.objects.get(username=username))
        if not (chat_user in self.chatuser_set.all()):
            chat_user.groups.add(self)

            notifications = Notifications.objects.create(chat_user=chat_user, group=self)
            notifications.save()

            chat_user.save()
        else:
            raise Exception('User already exists')

    def remove_user(self, username):
        chat_user = User.objects.get(username=username).chatuser#ChatUser.objects.filter(user__username=username).get()
        chat_user.groups.remove(self)

    def change_name(self, new_name):
        self.group_name = new_name
        self.save()

    def get_users(self):
        chatusers = [chatuser.user.username for chatuser in self.chatuser_set.all()]
        return ', '.join(chatusers)

class Notifications(models.Model):
    chat_user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    read = models.BooleanField(default=True)

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField()
    username = models.CharField(max_length=150)

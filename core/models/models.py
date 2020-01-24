from django.db import models
from django.contrib.auth.models import AbstractUser
from bleach import clean

class ChatUser(models.Model):
    groups = models.ManyToManyField(Group)

class Group(models.Model):
    group_name = models.CharField(max_length=150)
    last_message_time = models.DateField()

    def new_message(self, content, username):
        message = Message.objects.create(group=self, content=clean(content), username=username)
        message.save()


class Notifications(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    read = models.BooleanField(default=True)

class Message(models.Model):
    group = models.ForeignKey(group, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150)

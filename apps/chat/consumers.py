from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json

from core.models.models import Group

ERROR_COMMAND_MESSAGE = {
    'message': 'Invalid Command',
    'username': ''
}

class ChatAppConsumer(JsonWebsocketConsumer):

    def connect(self):

        user = scope['user']

        for group in user.groups:
            self.listen_to_group(group.id)

        self.accept()

    def disconnect(self):
        for group in user.groups:
            self.unlisten_to_group(group.id)

    def listen_to_group(self, group_id):
        async_to_sync(self.channel_layer.group_add)(
            group_id,
            self.channel_name
        )

    def unlisten_to_group(self, group_id):
        async_to_sync(self.channel_layer.group_discard)(
            group_id,
            self.channel_name
        )

    def group_send(self, group_id, payload):
        async_to_sync(self.channel_layer.group_send)(
            group_id,
            payload
        )

    def receive_json(self, data):

        e = data['type']

        if e == 'user': # events outside the scope chat group, such as opening a group
            self.receive_user_event(data['body'])
        elif e == 'group': # events within a chat group
            self.receive_chat_event(data['body'])
        else:
            raise 'Invalid message type!'

    def receive_user_event(self, body):

        chat_user = ChatUser.get_chat_user(self.scope['user'])

        if body['type'] == 'create':
            chat_user.create_group(body['command'])
        elif body['type'] == 'delete':
            chat_user.delete_group(body['command'])

        self.send(body['command'])

    def receive_chat_event(self, body):

        if body['type'] == 'message':
            self.chat_send_message(body['message'])
        elif body['type'] == 'command':
            self.receive_chat_special_command(body['command'])

    def receive_chat_special_command(self, command):

        # if invalid command, only send back to user
        group = Group.objects.get(id=command['group_id'])
        if command['type'] == 'add':
            group.add_user(command['group_id'], command['username'])
        elif command['type'] == 'change_name':
            group.change_name(command['new_name'])
        elif command['type'] == 'list': # individual group command
            self.send(
                ChatAppConsumer.create_message(
                    group.get_users(command['group_id']),
                    ''
                )
            )
        else:
            self.send(
                ERROR_COMMAND_MESSAGE
            )

    @staticmethod
    def create_message(message, username):
        return {
            'message': message,
            'username': username
        }

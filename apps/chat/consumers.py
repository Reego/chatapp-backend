from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json

from core.models.models import Group

# data['type'] = user or group
# data['body'] = {
#   type,
#   args
# }
#
#
#


# out going data
# {
#     'command': # false | true (add group / remove group / change name)
#     'message': # message - carries additional args
#     'username': # username
#     'group_id': # group_id
# }

class ChatAppConsumer(JsonWebsocketConsumer):

    # received incoming WebSocket connection
    def connect(self):

        user = self.scope['user']

        for group in user.chatuser.groups.all():
            self.listen_to_group(group.id)

        self.accept()

    # disconnects from WebSocket connection
    def disconnect(self):
        for group in user.groups:
            self.unlisten_to_group(group.id)

    # Subscribes this ChatAppConsumer instance to the channel
    def listen_to_group(self, group_id):
        async_to_sync(self.channel_layer.group_add)(
            group_id,
            self.channel_name
        )

    # Unsubscribes this ChatAppConsumer instance to the channel
    def unlisten_to_group(self, group_id):
        async_to_sync(self.channel_layer.group_discard)(
            group_id,
            self.channel_name
        )

    # Sends the payload to the channel specified by the given group_id
    def group_send(self, group_id, payload):
        async_to_sync(self.channel_layer.group_send)(
            group_id,
            payload
        )

    # Receives
    def receive_json(self, data):

        e = data['type']

        if e == 'USER': # events outside the scope chat group, such as opening a group -- only affect user
            self.receive_user_event(data['body'])
        elif e == 'CHAT': # events within a chat group
            self.receive_chat_event(data['body'])
        else:
            raise 'Invalid message type!'

    # receives and processes user events
    def receive_user_event(self, body):

        chat_user = ChatUser.get_chat_user(self.scope['user'])

        # initializes user's groups
        if body['type'] == 'INIT':
            groups_init = {
                'command': 'INIT',
                'groups': {},
            }
            for group in chat_user.groups:
                groups_init['groups'][group.id] = {
                    'group_id': group.id,
                    'group_name': group.group_name,
                    'messages': [{'message': message.content, 'username': message.username} for message in group.message_set.objects.all()],
                    'read':  chat_user.has_read(group.id),
                }
            this.send(groups_init)

        # creates group
        elif body['type'] == 'CREATE':
            default_group_name = 'New Group'

            group = chat_user.create_group(default_group_name)

            self.send(ChatAppConsumer.out('GROUP_CREATE', group.id, default_group_name))
            self.send(ChatAppConsumer.out('MESSAGE', group.id, 'Group created'))

        # removes user from group and deletes group if no other users are in it
        elif body['type'] == 'DELETE':
            chat_user.delete_group(body['group_id'])

            self.send(ChatAppConsumer.out('GROUP_DELETE', body['group_id']))

    # processes top-level chat events
    def receive_chat_event(self, body):

        # standard message
        if body['type'] == 'MESSAGE':

            group = Group.objects.get(id=command['group_id'])
            username = body['username']
            message = body['message']
            group.send_message(message, username)
            self.send(ChatAppConsumer.out('MESSAGE', group.id, message, username))

        # special chat command
        elif body['type'] == 'COMMAND':
            self.receive_chat_special_command(body['command'])

    # processes special chat commands
    def receive_chat_special_command(self, command):

        # if invalid command, only send back to user
        group = Group.objects.get(id=command['group_id'])

        # adds user to group
        if command['type'] == 'ADD':
            message = 'Added ' + command['username'] + ' to the group.'

            group.add_user(command['group_id'], command['username'])
            group.send_message(message)

            self.send(ChatAppConsumer.out('MESSAGE', group.id, message))

        # changes group name
        elif command['type'] == 'CHANGE_NAME':
            new_name = command['new_name']
            message = 'Group name has been changed'

            group.change_name(new_name)
            group.send_message(message)

            self.send(ChatAppConsumer.out('GROUP_NAME_CHANGE', group.id, new_name))
            self.send(ChatAppConsumer.out('MESSAGE', group.id, message))

        # lists users in group
        elif command['type'] == 'LIST': # individual group command
            self.send(ChatAppConsumer.out('MESSAGE', group.id, group.get_users()))
        # invalid command
        else:
            self.send(ChatAppConsumer.out('MESSAGE', group.id, 'Invalid Command'))

    @staticmethod
    def out(command_type, group_id, message='', username=''):
        return {
            'command_type': command_type,
            'group_id': group_id,
            'message': message,
            'username': username,
        }

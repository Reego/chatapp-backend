from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json

from core.models import ChatUser, Group

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

        self.user = self.scope['user']

        self.chatuser = ChatUser.get_chat_user(self.user)

        for group in self.chatuser.groups.all():
            self.listen_to_group(group.id)

        self.accept()

    # disconnects from WebSocket connection
    def disconnect(self, close_code):
        for group in self.user.groups.all():
            self.unlisten_to_group(group.id)

    # Subscribes this ChatAppConsumer instance to the channel
    def listen_to_group(self, group_id):
        print(str(group_id) + '\n\n\n\n')
        async_to_sync(self.channel_layer.group_add)(
            str(group_id),
            self.channel_name
        )

    # Unsubscribes this ChatAppConsumer instance to the channel
    def unlisten_to_group(self, group_id):
        async_to_sync(self.channel_layer.group_discard)(
            str(group_id),
            self.channel_name
        )

    # Sends the payload to the channel specified by the given group_id
    def group_send(self, group_id, payload):
        print('\n\nGROUP SEND TO ' + str(group_id))
        async_to_sync(self.channel_layer.group_send)(
            str(group_id),
            payload
        )
        # async_to_sync(self.channel_layer.group_send)(
        #     str(group_id),
        #     json.dumps(payload)
        # )

    # Receives
    def receive_json(self, data):

        e = data['type']

        if e == 'USER': # events outside the scope chat group, such as opening a group -- only affect user
            self.receive_user_event(data['body'])
        elif e == 'CHAT': # events within a chat group
            print(data['body'])
            self.receive_chat_event(data['body'])
        elif e == 'INIT':
            self.receive_user_event(data)
        else:
            print(data)
            raise 'Invalid message type!'

    # receives and processes user events
    def receive_user_event(self, body):

        # chat_user = ChatUser.get_chat_user(self.user)

        # initializes user's groups
        if body['type'] == 'INIT':
            # print('\n\nINIT222\n\n')
            groups_init = {
                'command_type': 'INIT',
                'groups': {},
            }
            # print('\n\nINIT---55\n\n')
            for group in self.chatuser.groups.all():
                groups_init['groups'][group.id] = {
                    'group_id': group.id,
                    'group_name': group.group_name,
                    'messages': [{'message': message.content, 'username': message.username} for message in group.message_set.all()],
                    'read':  self.chatuser.has_read(group.id),
                }

            # print('\n\nINIT----6\n\n')
            self.sendObj(groups_init)

        # creates group
        elif body['type'] == 'CREATE':
            # print('\n\n\nHUH?')
            default_group_name = 'New Group'

            group = self.chatuser.create_group(default_group_name)

            self.sendObj(ChatAppConsumer.out('GROUP_CREATE', group.id, default_group_name))
            self.sendObj(ChatAppConsumer.out('MESSAGE', group.id, 'Group created'))

        # removes user from group and deletes group if no other users are in it
        elif body['type'] == 'DELETE':
            self.chatuser.delete_group(body['group_id'])
            self.chatuser.save()
            self.sendObj(ChatAppConsumer.out('GROUP_DELETE', body['group_id']))
        elif body['type'] == 'READ':
            notifications = self.chatuser.get_notifications_obj(body['group_id'])
            notifications.read = True
            notifications.save()

    # processes top-level chat events
    def receive_chat_event(self, body):

        # standard message
        if body['type'] == 'MESSAGE':

            group = Group.objects.get(id=body['group_id'])
            username = body['username']
            message = body['message']
            group.send_message(message, username)
            self.group_send(group.id, ChatAppConsumer.out('MESSAGE', group.id, message, username))

        # special chat command
        elif body['type'] == 'COMMAND':
            self.receive_chat_special_command(body)

    # processes special chat commands
    def receive_chat_special_command(self, command):

        # if invalid command, only send back to user
        group = Group.objects.get(id=command['group_id'])

        print(group)

        # adds user to group
        if command['command'] == 'ADD':
            message = 'Added ' + command['username'] + ' to the group.'

            group.add_user(command['username'])
            group.send_message(message)

            self.group_send(group.id, ChatAppConsumer.out('MESSAGE', group.id, message))

        # changes group name
        elif command['command'] == 'CHANGE_NAME':

            new_name = command['username']
            message = 'Group name has been changed'

            group.change_name(new_name)
            group.send_message(message)

            self.group_send(group.id, ChatAppConsumer.out('GROUP_NAME_CHANGE', group.id, new_name))
            self.group_send(group.id, ChatAppConsumer.out('MESSAGE', group.id, message))

        # lists users in group
        elif command['command'] == 'LIST': # individual group command
            self.sendObj(ChatAppConsumer.out('MESSAGE', group.id, group.get_users()))
        # invalid command
        else:
            self.sendObj(ChatAppConsumer.out('MESSAGE', group.id, 'Invalid Command'))

    def sendObj(self, obj):
        self.send(text_data=json.dumps(obj))

    def chat_message(self, obj):
        self.sendObj(obj)

    @staticmethod
    def out(command_type, group_id, message='', username='', type=''):
        return {
            'command_type': command_type,
            'group_id': str(group_id),
            'message': message,
            'username': username,
            'type': 'chat_message',
        }

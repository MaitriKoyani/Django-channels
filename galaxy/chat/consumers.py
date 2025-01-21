# # import json

# # from channels.generic.websocket import AsyncWebsocketConsumer


# # class ChatConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
# #         self.room_group_name = f"chat_{self.room_name}"

# #         # Join room group
# #         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

# #         await self.accept()

# #     async def disconnect(self, close_code):
# #         # Leave room group
# #         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

# #     # Receive message from WebSocket
# #     async def receive(self, text_data):
# #         text_data_json = json.loads(text_data)
# #         message = text_data_json["message"]

# #         # Send message to room group
# #         await self.channel_layer.group_send(
# #             self.room_group_name, {"type": "chat.message", "message": message}
# #         )

# #     # Receive message from room group
# #     async def chat_message(self, event):
# #         message = event["message"]

# #         # Send message to WebSocket
# #         await self.send(text_data=json.dumps({"message": message}))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, GrpUser, MessageContent, Group, User

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # user = self.scope.get("user")  # Assuming user is already attached via middleware
#         user = User.objects.get(username='Maitri')
#         # Check if the user is part of the group
#         try:
#             group = Group.objects.get(name=self.room_name)
#             grp_user = GrpUser.objects.get(group=group, user=user)
#         except (Group.DoesNotExist, GrpUser.DoesNotExist):
#             # If user is not part of the group, reject the connection
#             await self.close()
#             return

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Find or create the MessageContent
#         message_content = MessageContent.objects.create(content=message)

#         # Find the user and group
#         user = self.scope.get("user")
#         group = Group.objects.get(name=self.room_name)
#         grp_user = GrpUser.objects.get(group=group, user=user)

#         # Create the ChatMessage
#         chat_message = ChatMessage.objects.create(
#             grp_user=grp_user,
#             message_content=message_content
#         )

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))
from asgiref.sync import sync_to_async
from .models import User, ChatMessage, MessageContent, Group, GrpUser
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Use sync_to_async to perform the database query
        self.user = await sync_to_async(self.get_user)("Maitri")

        if self.user:
            print(f"User {self.user.username} connected to room {self.room_name}")
        else:
            print("Unauthenticated user attempted to connect")
            await self.close()  # Close connection if unauthenticated

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Send chat history to WebSocket when connecting
        await self.send_chat_history()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Create the message content in the database asynchronously
        message_content = await sync_to_async(MessageContent.objects.create)(content=message)

        # Find the user and group asynchronously
        user = await sync_to_async(self.get_user)("Maitri")
        group = await sync_to_async(Group.objects.get)(name=self.room_name)
        
        try:
            grp_user = await sync_to_async(GrpUser.objects.get)(group=group, user=user)
        except GrpUser.DoesNotExist:
            print(f"User {user.username} is not part of the group {self.room_name}.")
            return  # Exit early if user is not part of the group

        # Create the ChatMessage in the database asynchronously
        await sync_to_async(ChatMessage.objects.create)(
            grp_user=grp_user,
            message_content=message_content
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    # Helper method to retrieve user from the database
    def get_user(self, user):
        if user:
            return User.objects.get(username=user)
        return None

    # Send chat history to the WebSocket client
    async def send_chat_history(self):
    # Get the group asynchronously
        group = await sync_to_async(Group.objects.get)(name=self.room_name)
        
        grp_user_queryset = await sync_to_async(GrpUser.objects.filter)(group=group)(all)

        messages = await sync_to_async(ChatMessage.objects.filter)(grp_user_id=grp_user_queryset)(all)

        for chat_message in messages:
            message_data = chat_message.message_content.content
            await self.send(text_data=json.dumps({
                "message": message_data
            }))

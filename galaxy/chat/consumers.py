from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import User, ChatMessage, MessageContent, Group, GrpUser
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Use sync_to_async to perform the database query
        self.user = await sync_to_async(self.get_user)("hasti")

        if self.user:
            print(f"User {self.user.username} connected to room {self.room_name}")
        else:
            print("Unauthenticated user attempted to connect")
            await self.close()  # Close connection if unauthenticated

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send chat history to WebSocket when connecting
        await self.send_chat_history()

        

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        message_content = await sync_to_async(MessageContent.objects.create)(content=message)
        
        user = await sync_to_async(self.get_user)("hasti")
        group = await sync_to_async(Group.objects.get)(name=self.room_name)
        
        try:
            grp_user = await sync_to_async(GrpUser.objects.get)(group=group, user=user)
        except GrpUser.DoesNotExist:
            print(f"User {user.username} is not part of the group {self.room_name}.")
            return  

        await sync_to_async(ChatMessage.objects.create)(
            grp_user=grp_user,
            message_content=message_content
        )

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))

    def get_user(self, user):
        if user:
            return User.objects.get(username=user)
        return None

    async def send_chat_history(self):

        group = await sync_to_async(Group.objects.get)(name=self.room_name)
        
        grp_user_queryset = await sync_to_async(list)(GrpUser.objects.filter(group=group))
        
        messages = []

        for gu in grp_user_queryset:
        
            messages += await sync_to_async(lambda: list(ChatMessage.objects.filter(grp_user_id=gu)))()
        
        messages = sorted(messages, key=lambda x: x.created_at)
        for chat_message in messages:
            message_data = await sync_to_async(lambda: chat_message.message_content.content)()
            sender = await sync_to_async(lambda: chat_message.grp_user.user.username)()
            await self.send(text_data=json.dumps({
                "message": message_data,
                "sender": sender
            }))

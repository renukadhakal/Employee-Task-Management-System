import json
from channels.generic.websocket import AsyncWebsocketConsumer
from account.models import User
from asgiref.sync import sync_to_async
from .models import Message
from notification.models import Notification


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        self.other = self.scope["url_route"]["kwargs"]["username"]
        self.room_name = f"chat_{'_'.join(sorted([self.me.username, self.other]))}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        receiver = await sync_to_async(User.objects.get)(username=self.other)

        await sync_to_async(Message.objects.create)(
            sender=self.me, receiver=receiver, message=message
        )

        await sync_to_async(Notification.objects.create)(
            title=f"You have got a Message from {self.me.username}",
            user=receiver,
            message=message,
        )

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "user": self.me.username,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "user": event["user"],
                }
            )
        )


class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        self.room_name = f"chat_bot_{self.me.username}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        from account.models import User

        bot_user = await sync_to_async(User.objects.get)(username="TaskBot")

        await sync_to_async(Message.objects.create)(
            sender=self.me, receiver=bot_user, message=message
        )

        # Ask the bot (sync call inside async)
        from .views import ask_bot

        bot_reply = await sync_to_async(ask_bot)(message)

        await sync_to_async(Message.objects.create)(
            sender=bot_user, receiver=self.me, message=bot_reply
        )

        await self.send(json.dumps({"message": message, "user": self.me.username}))
        await self.send(json.dumps({"message": bot_reply, "user": bot_user.username}))

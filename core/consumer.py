import json

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.chat.tasks import process_chat


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notification", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notification", self.channel_name)

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"chat_{self.user.id}"

        await self.accept()
        await self.channel_layer.group_add("chat", self.channel_name)
       

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        user = self.scope['user']
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")

        process_chat(message, user)



    async def send_message(self, event):
        message = event["message"]
        scholarships = event["scholarships"]
        await self.send(text_data=json.dumps({"message": message, "scholarships": scholarships}))
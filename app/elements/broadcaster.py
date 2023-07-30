import asyncio
from collections import deque
import logging

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class Message:
    def __init__(self, sender, receiver, text):
        self.sender = sender
        self.receiver = receiver
        self.text = text

    @property
    def as_dict(self):
        return {"From": self.sender, "To": self.receiver, "Body": self.text}


class Broadcaster:
    def __init__(
        self,
        message_generator,
        web_client,
        settings,
        interval=10,
    ):
        self.message_generator = message_generator
        self.web_client = web_client
        self.interval = interval
        self.settings = settings
        self.outbound_messages = deque()

    async def send_messages(self):
        while self.outbound_messages:
            m = self.outbound_messages.popleft()
            async with self.web_client.post(
                self.settings.twilio_endpoint, timeout=1, data=m.as_dict()
            ) as response:
                if response.status >= 400:
                    try:
                        reason = await response.json()
                    except:
                        reason = await response.text()

                    log.error(f"failed with reason: [{reason}]")
                    continue

                response = await response.json()

    async def run_forever(self):
        while True:
            async for receiver_number, message_text in self.message_generator():
                self.outbound_messages.append(
                    Message(
                        self.settings.from_number,
                        receiver_number,
                        message_text,
                    )
                )
                log.info(
                    f"created message: [{message_text.body}] for receiver: [{receiver_number}]..."
                )

            await self.send_messages()

            await asyncio.sleep(self.interval)

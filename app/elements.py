import asyncio
from collections import deque
import csv
from itertools import count
import logging
import os


log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class Dataset:
    def __init__(self, filepath):
        self.filepath = filepath

    def __iter__(self):
        raise NotImplementedError()

    @staticmethod
    def read(filepath):
        """load dataset from source"""


class CSVDataset(Dataset):
    @staticmethod
    def read(filepath):
        abs_filepath = os.path.join(os.getcwd(), filepath)
        with open(abs_filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

    def __iter__(self):
        for row in self.read(self.filepath):
            yield row


class Message:
    def __init__(self, sender, receiver, text, reference):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.reference = reference

    @property
    def body(self):
        return f'{self.text} - {self.reference}'

    @property
    def as_dict(self):
        return {'From': self.sender, 'To': self.receiver, 'Body': self.body}

    @classmethod
    def from_csv_row(cls, sender, receiver, row):
        return cls(sender, receiver, *row)


class MessagingService:
    def __init__(
        self,
        dataset,
        web_client,
        endpoint,
        from_phonenumber,
        interval=10
    ):
        self.dataset = dataset
        self.web_client = web_client
        self.interval = interval
        self.endpoint = endpoint
        self.from_ = from_phonenumber

        self.tokens = count(1, 2)
        self.outbound_messages = deque()
        self.receivers = dict()

    def register_receiver(self, receiver_number):
        self.receivers[next(self.tokens)] = receiver_number

    async def send_messages(self):
        while self.outbound_messages:
            m = self.outbound_messages.popleft()
            async with self.web_client.post(
                self.endpoint,
                timeout=1,
                data=m.as_dict
            ) as response:
                if response.status >= 400:
                    try:
                        reason = await response.json()
                    except:
                        reason = await response.text()

                    log.error(f'failed with reason: [{reason}]')
                    continue

                response = await response.json()

    async def run_forever(self):
        dataset_iterable = iter(self.dataset)
        while True:
            try:
                row = next(dataset_iterable)
            except StopIteration:
                log.info(f'no more records in the source dataset..')
                return

            for receiver_id, receiver_number in self.receivers.items():
                message = Message.from_csv_row(
                    self.from_, receiver_number, row)
                self.outbound_messages.append(message)
                log.info(
                    f'created message: [{message.body}] for receiver: [{receiver_id}]...')

            await self.send_messages()

            await asyncio.sleep(self.interval)

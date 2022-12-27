import asyncio
import aiohttp
from pydantic import BaseSettings, Field
from app.elements import CSVDataset, MessagingService


class Settings(BaseSettings):
    account_sid: str = Field(..., env='TWILIO_ACCOUNT_SID')
    auth_token: str = Field(..., env='TWILIO_AUTH_TOKEN')
    from_number: str = Field(..., env='TWILIO_FROM_PHONENUMBER')
    receivers: list = Field(..., env='TWILIO_RECEIVER_PHONENUMBERS')


API_ENDPOINT_FORMAT = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'


def main(interval, filepath):
    settings = Settings()
    basic_auth = aiohttp.BasicAuth(settings.account_sid, settings.auth_token)

    dataset = CSVDataset(filepath)

    web_client = aiohttp.ClientSession(
        auth=basic_auth,
        connector=aiohttp.TCPConnector(limit_per_host=4)
    )

    service = MessagingService(
        dataset,
        web_client,
        API_ENDPOINT_FORMAT.format(settings.account_sid),
        settings.from_number,
        interval=interval,
        auth=basic_auth
    )

    for phonenumber in settings.receivers:
        service.register_receiver(phonenumber)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(service.run_forever())
    finally:
        loop.run_until_complete(web_client.close())
        loop.close()

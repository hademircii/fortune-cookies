import asyncio
import aiohttp
from pydantic import Field
from pydantic_settings import BaseSettings
from .broadcaster import Broadcaster
from .consumer import AsyncFortuneCookie

API_ENDPOINT_FORMAT = (
    "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
)


class Settings(BaseSettings):
    account_sid: str = Field(..., alias="TWILIO_ACCOUNT_SID")
    auth_token: str = Field(..., alias="TWILIO_AUTH_TOKEN")
    from_number: str = Field(..., alias="TWILIO_FROM_PHONENUMBER")
    api_key: str = Field(..., alias="FORTUNE_COOKIE_API_KEY")

    @property
    def twilio_endpoint(self):
        return API_ENDPOINT_FORMAT.format(self.account_sid)


def main(interval, server_address):
    settings = Settings()
    basic_auth = aiohttp.BasicAuth(settings.account_sid, settings.auth_token)

    mobile_client = aiohttp.ClientSession(
        auth=basic_auth,
        connector=aiohttp.TCPConnector(limit_per_host=4),
    )

    quote_client = AsyncFortuneCookie(server_address, api_key=settings.api_key)

    service = Broadcaster(
        quote_client,
        mobile_client,
        settings=settings,
        interval=interval,
    )

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(service.run_forever())
    finally:
        loop.run_until_complete(mobile_client.close())
        loop.close()

import aiohttp
from typing import AsyncGenerator, Tuple
from .api import PhoneNumber, Quote


class AsyncFortuneCookie:
    def __init__(self, server_address: str):
        self.server_address = server_address

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=2)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def __aiter__(self) -> AsyncGenerator[PhoneNumber, None]:
        async for phone_number in self.paginate_phone_numbers(page_size=10):
            yield phone_number

    async def paginate_phone_numbers(
        self, page_size: int = 10
    ) -> AsyncGenerator[PhoneNumber, None]:
        page = 1
        total_pages = None
        while True:
            async with self.session.get(
                f"{self.server_address}/phone_numbers",
                params={"page_size": page_size, "page": page},
            ) as response:
                if response.status >= 400:
                    raise Exception(await response.text())
                response_data = await response.json()
                if total_pages is None:
                    total_pages = response_data["total_pages"]

                for phone_number in response_data["results"]:
                    yield PhoneNumber(**phone_number)

                page += 1
                if page > total_pages:
                    break

    async def get_random_quote(self) -> Quote:
        async with self.session.get(
            f"{self.server_address}/quotes/random"
        ) as response:
            if response.status >= 400:
                raise Exception(await response.text())
            response_data = await response.json()
            return Quote(**response_data)


async def a_message_for_each(
    server_address,
) -> AsyncGenerator[Tuple[PhoneNumber, Quote]]:
    async with AsyncFortuneCookie(server_address) as client:
        quote = await client.get_random_quote()
        async for phone_number in client:
            yield phone_number, quote

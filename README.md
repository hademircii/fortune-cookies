# Fortune Cookie Wisdom

an app that texts you curated quotes, periodically.

## The App
Uses my favourite libraries like FastAPI, Pydantic and SQLAlchemy, together in
a server to manage queotes and receivers.
there is a consumer built with asyncio and aiottp, managed by a main module and runs
forever. some techniques for async programming, object-oriented design and
error handling are there with the style of Python I enjoy.

## Running the Application

Using Docker, you can easily set up and run the application:

```bash
$ docker-compose up
```

Ensure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed. The application also requires Twilio account credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_PHONENUMBER`) and
an api key (`FORTUNE_COOKIE_API_KEY`).

## Steps to Run

1. Clone the repository.
2. Rename `.env.sample` to `.env` and add your Twilio credentials.
3. Run `docker-compose up`.

You'll need an API key to register your phone number and start receiving quotes.

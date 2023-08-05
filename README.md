# Fortune Cookie Wisdom

Embark on a journey through literature and wisdom with Fortune Cookie Wisdom, a curated mobile delivery system for thought-provoking quotes.

## Design and Capabilities

 asynchronous programming, HTTP communication, object-oriented design, error handling, and logging. The architecture involves a PostgreSQL database, an API server, and a periodic consumer service, creating an ecosystem that delivers quotes to registered phone numbers.

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

FROM python:3.9

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app
WORKDIR /app

ENV INTERVAL 10

RUN chmod +x ./bin/entrypoint.sh

CMD bash ./bin/entrypoint.sh

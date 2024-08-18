FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y whois && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./src/ .

CMD python3  app.py
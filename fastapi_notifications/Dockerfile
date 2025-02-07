FROM python:3.11

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./src/requirements.txt .

RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir -r requirements.txt

COPY entrypoint-fastapi.sh /
RUN chmod +x /entrypoint-fastapi.sh

COPY entrypoint-celery.sh /
RUN chmod +x /entrypoint-celery.sh

COPY ./src .
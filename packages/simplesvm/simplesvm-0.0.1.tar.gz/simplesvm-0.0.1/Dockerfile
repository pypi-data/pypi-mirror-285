FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false

FROM python:3.12-slim

RUN pip install uvicorn gunicorn poetry wheel virtualenv

WORKDIR /usr/src/api

COPY ./pyproject.toml ./poetry.lock* /usr/src/api/
COPY . /usr/src/api

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

EXPOSE 8000

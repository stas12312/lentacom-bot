FROM python:3.9.7-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get -y update
RUN apt-get -y install zbar-tools curl libzbar-dev

RUN pip install poetry

# Установка зависимостей
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry update && poetry install


# Копирование исходного кода
COPY ./app /app

# Копирование скрипта подгтовки запуска приложения
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "bot.py"]

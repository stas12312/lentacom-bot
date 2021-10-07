FROM python:3.9.7-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade
RUN apt-get install zbar-tools curl -y

RUN pip install poetry

# Установка зависимостей
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry update && poetry install


# Копирование исходного кода
COPY ./app /app

# Копирование скрипта подгтовки запуска приложения
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "bot.py"]

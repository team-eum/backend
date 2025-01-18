FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get install -y --no-install-recommends pkg-config build-essential default-libmysqlclient-dev mariadb-client \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
RUN chmod +x /app/docker-entrypoint.sh
RUN if [ -d "/app/static" ]; then chmod -R 755 /app/static; fi
EXPOSE 8000
CMD ["/app/docker-entrypoint.sh"]
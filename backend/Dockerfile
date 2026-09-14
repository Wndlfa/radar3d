FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml ./
# Alpine usa musl: alguns pacotes (psycopg, etc.) compilam do fonte.
# libpq fica no runtime; build-base/dev só durante o pip install.
RUN apk add --no-cache libpq && \
    apk add --no-cache --virtual .build-deps build-base musl-dev postgresql-dev libffi-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    apk del .build-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "radar3d.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

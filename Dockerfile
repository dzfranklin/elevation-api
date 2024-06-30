FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.1

WORKDIR /app

ENV LANG C.UTF-8

RUN apt update; \
    apt install -y --no-install-recommends \
      ca-certificates netbase tzdata \
      gcc g++ \
      python3-full python3-pip python3-dev; \
    rm -rf /var/lib/apt/lists/*

ENV \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

ENV \
  POETRY_NO_INTERACTION=1 \
  POETRY_NO_ANSI=1 \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

RUN pip install poetry==1.8.3 --break-system-packages

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-directory

COPY . .
RUN poetry install --only main

ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", \
  "--host", "0.0.0.0", \
  "--port", "80", \
  "--proxy-headers" \
]

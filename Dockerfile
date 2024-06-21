FROM python

WORKDIR /app

RUN apt update && apt install -y gdal-bin libgdal-dev

ENV \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_NO_ANSI=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-directory

COPY . .
RUN poetry install --only main

ENTRYPOINT ["uvicorn", "main:app", \
  "--host", "0.0.0.0", \
  "--port", "80", \
  "--proxy-headers",
]

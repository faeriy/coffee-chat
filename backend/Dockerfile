# Use Python version that matches pyproject.toml
FROM python:3.12-slim

WORKDIR /app

# Only curl needed for Poetry installer (psycopg2-binary uses wheels, no build)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (match version that generated poetry.lock)
ENV POETRY_VERSION=2.2.1
ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN curl -sSL https://install.python-poetry.org | python3 -

# Disable virtualenv inside container; install deps into system Python
RUN poetry config virtualenvs.create false

# Copy dependency manifests first (better layer caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies only (no dev group)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

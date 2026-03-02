FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project

COPY src/ src/
COPY scripts/ scripts/
RUN uv sync --no-dev

EXPOSE 8000 8001 8002 8003 8004

CMD ["uv", "run", "python", "scripts/start.py"]

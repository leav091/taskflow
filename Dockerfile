FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml ./
RUN uv sync --no-install-project --no-dev
COPY backend ./backend
COPY README.md ./README.md
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "backend.server.main:app", "--host", "0.0.0.0", "--port", "8000"]

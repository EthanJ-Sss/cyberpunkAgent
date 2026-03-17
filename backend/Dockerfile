FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY src/ src/

RUN uv venv && uv pip install .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "cybermarket.main:app", "--host", "0.0.0.0", "--port", "8000"]

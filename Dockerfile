FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files first for caching
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction

# Copy source
COPY . .

EXPOSE 8000
CMD ["poetry", "run", "python", "run.py"]

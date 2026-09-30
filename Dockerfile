FROM python:3.14-slim

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Copy requirements first so Docker can cache the install step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user (safer)
RUN useradd -m appuser && chown -R appuser /code
USER appuser

EXPOSE 8000
# Cloud hosts set $PORT; locally it falls back to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
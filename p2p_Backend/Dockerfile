FROM python:3.12-slim

# Don't buffer stdout, so `docker compose logs -f backend` shows output live.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Requirements are copied first so this layer only rebuilds when dependencies
# change — editing app code then skips the slow pip install.
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

COPY . .

# Run as a non-root user. Nothing in the app writes to disk (state lives in
# MySQL), so the image can stay read-only to the process.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# python instead of curl — the slim image ships neither curl nor wget, and
# this avoids an apt-get layer just for a health check.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
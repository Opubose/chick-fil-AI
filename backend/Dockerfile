FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/

# Just in case
RUN rm -rf /app/api/__pycache__

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--pythonpath", "/app/api", "app:app"]

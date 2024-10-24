FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ /app/api/
# Just in case
RUN rm -rf /app/api/__pycache__
RUN pip install gunicorn
WORKDIR /app/api
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT:-8000}", "app:app"]

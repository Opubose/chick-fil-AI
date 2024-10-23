FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/

# Just in case
RUN rm -rf /app/api/__pycache__

CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/

# just in case
RUN rm -rf /app/api/__pycache__

# Expose the flask default port
EXPOSE 8000

# Set environment variables (optional, customize as needed)
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=development

# Command to run the Flask app (adjust this if you use a different entry point)
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

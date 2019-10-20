FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt /app
COPY sevilla /app/sevilla
COPY migrations /app/migrations
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["gunicorn", "sevilla:create_app()", "-b", "0.0.0.0:8080"]

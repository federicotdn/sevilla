FROM python:3.7-slim

COPY requirements.txt .
COPY LICENSE .
COPY sevilla sevilla
COPY migrations migrations
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["gunicorn", "sevilla:create_app()", "-b", "0.0.0.0:8080"]

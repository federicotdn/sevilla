dev_server:
	FLASK_APP=sevilla \
	FLASK_ENV=development \
	SECRET_KEY=dev-secret-key \
	SESSION_COOKIE_SECURE=False \
	flask run --port 8080

lint:
	flake8 sevilla/
	black --check sevilla/

formatter:
	black sevilla/

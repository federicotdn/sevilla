DEV_PASSWORD=sevilla

dev_server:
	FLASK_APP=sevilla \
	FLASK_ENV=development \
	SECRET_KEY=dev-secret-key \
	SESSION_COOKIE_SECURE=False \
	SEVILLA_PASSWORD=$(DEV_PASSWORD) \
	flask run --port 8080

lint:
	flake8 sevilla/
	black --check sevilla/

formatter:
	black sevilla/

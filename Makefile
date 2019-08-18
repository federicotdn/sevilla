DEV_PASSWORD=sevilla

dev_server:
	FLASK_APP=sevilla \
	FLASK_ENV=development \
	SECRET_KEY=dev-secret-key \
	SESSION_COOKIE_SECURE=False \
	SEVILLA_PASSWORD=$(DEV_PASSWORD) \
	flask run --port 8080

shell:
	FLASK_APP=sevilla \
	SEVILLA_PASSWORD=$(DEV_PASSWORD) \
	flask shell

lint:
	flake8 sevilla/
	black --check sevilla/

format:
	black sevilla/

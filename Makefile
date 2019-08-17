dev_server:
	FLASK_APP=sevilla FLASK_ENV=development flask run --port 8080

lint:
	flake8 sevilla/
	black --check sevilla/

formatter:
	black sevilla/

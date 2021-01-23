# sync_calendars

* start rabbitmq: `docker-compose up rabbitmq`
* start celery worker: `celery worker -A app:celery -l info -f celery.log`
* build static files: `npm run start`
* start webapp: `flask run --cert=certs/localhost.pem --key=certs/localhost-key.pem`

"""Application entry point."""
from sync_calendars import create_app

app = create_app()
if __name__ == "__main__":
    if app.config['FLASK_ENV'] == 'development':
        print('start with SSL')
        app.run(ssl_context=('certs/localhost.pem', 'certs/localhost-key.pem'))
    else:
        print('start without SSL')
        app.run()

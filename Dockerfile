FROM python:3.7-slim-buster as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# Install runtime dependencies
RUN apt update && apt install -y libpq5

FROM base AS python-deps

RUN apt-get install build-essential libssl-dev libffi-dev
RUN pip install cryptography

# Install pipenv and compilation dependencies
RUN pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --skip-lock

##########################################
# Build frontend
##########################################
FROM node:14 as frontend-build

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
WORKDIR /usr/app

# Install application into container
COPY . .
COPY --from=frontend-build ./sync_calendars/static sync_calendars/static

# Run the application
CMD [ "gunicorn", "-b 0.0.0.0:5000", "sync_calendars.app:create_app()"]
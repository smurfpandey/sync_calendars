#!/bin/bash

# start rabbitmq
docker-compose up -d

# start python app
python wsgi.py
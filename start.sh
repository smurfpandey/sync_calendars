#!/usr/bin/env bash
#
# Bash script to startup all components of ghost blog, mostly through
# docker and checking if services are available using wait-for-it

start() {
    docker-compose up -d rabbitmq
    docker-compose run --rm wait_for_it rabbitmq:5672 --timeout=20 --strict -- echo "rabbitmq is up"

    if [[ $? -gt 0 ]] ; then
        exit 124
    fi

    docker-compose up -d db
    docker-compose run --rm wait_for_it db:5432 --timeout=10 --strict -- echo "db is up"

    if [[ $? -gt 0 ]] ; then
        exit 124
    fi

    docker-compose up -d worker
    docker-compose up app
}

stop() {
    docker-compose stop
}

restart() {
    stop
    start
}

case $1 in
    start) start;;
    stop) stop;;
    restart) restart;;
    "") start;;
    *) echo "Usage: ./service start|stop|restart"
esac

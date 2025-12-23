#!/bin/sh
yoyo apply -vvv --batch --database mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE} /app/migrations
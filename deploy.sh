#!/bin/sh

set -e

# Push new image
docker build -t joonhyung/jjalbot:latest .
printf "%s" "${DOCKER_PASSWORD}" | docker login --username "${DOCKER_USER}" --password-stdin
docker push joonhyung/jjalbot:latest

# Pull the new image
# X_REGISTRY_AUTH=$(printf '{
#   "username": "%s",
#   "password": "%s"
# }' "${DOCKER_USER}" "${DOCKER_PASSWORD}" | base64)
curl -X POST -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     "${DOCKER_API_URL}/images/joonhyung%2Fjjalbot%3Alatest/tag?repo=joonhyung%2Fjjalbot&tag=legacy"
curl -f -X POST -H "Authorization: Bearer ${DOCKER_API_TOKEN}" -H "X-Registry-Auth: ${X_REGISTRY_AUTH}" \
     "${DOCKER_API_URL}/images/create?fromImage=joonhyung%2Fjjalbot%3Alatest"

# Recreate container through Docker Engine API
curl -X POST -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     "${DOCKER_API_URL}/containers/jjalbot/stop"
curl -X DELETE -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     "${DOCKER_API_URL}/containers/jjalbot"
curl -f -X POST -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     -H "Content-type: application/json" \
     -d \
      "{
           \"Image\": \"joonhyung/jjalbot:latest\",
           \"Volumes\": {
               \"/var/jjalbot\": {}
           },
           \"HostConfig\": {
               \"Binds\": [\"jjalbot_data:/var/jjalbot\"]
           },
           \"NetworkingConfig\": {
               \"EndpointsConfig\": {
                   \"run\": {}
               }
           },
           \"Env\": [
               \"SLACK_APP_SIGNING_SECRET=${SLACK_APP_SIGNING_SECRET}\",
               \"DJANGO_SETTINGS_MODULE=jjalbot.settings.production\",
               \"SECRET_KEY=${SECRET_KEY}\",
               \"DB_HOST=${DB_HOST}\",
               \"DB_NAME=${DB_NAME}\",
               \"DB_USER=${DB_USER}\",
               \"DB_PASSWORD=${DB_PASSWORD}\",
               \"DB_PORT=${DB_PORT}\",
               \"CELERY_BROKER_USER=${CELERY_BROKER_USER}\",
               \"CELERY_BROKER_PASSWORD=${CELERY_BROKER_PASSWORD}\",
               \"CELERY_BROKER_HOST=${CELERY_BROKER_HOST}\",
               \"CELERY_BROKER_VHOST=${CELERY_BROKER_VHOST}\",
               \"CELERY_BROKER_URL=${CELERY_BROKER_URL}\"
           ]
       }" \
     "${DOCKER_API_URL}/containers/create?name=jjalbot"
curl -f -X POST -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     "${DOCKER_API_URL}/containers/jjalbot/start"
     
# Delete the old image
curl -X DELETE -H "Authorization: Bearer ${DOCKER_API_TOKEN}" \
     "${DOCKER_API_URL}/images/joonhyung%2Fjjalbot%3Alegacy"

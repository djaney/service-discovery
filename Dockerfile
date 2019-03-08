FROM python:3.7.2-alpine3.7
ARG env=production
COPY . /app
WORKDIR /app
RUN apk add --update graphviz  && \
    pip install -r requirements.txt && \
    if [ "${env}" = "test" ]; then pip install pytest; fi
EXPOSE 5000
ENTRYPOINT ./registry.py --heartbeat 30
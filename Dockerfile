FROM python:3.7.2-alpine3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ./registry.py --heartbeat 30
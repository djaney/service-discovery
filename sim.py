#!/usr/bin/env python3
from flask import Flask
import argparse
from threading import Thread, Event
from urllib import request
import json
import random
import atexit

app = Flask(__name__)


@app.route('/healthcheck')
def healthcheck():
    return '', 200


parser = argparse.ArgumentParser(description='Start Service')
parser.add_argument('name', help="service name", type=str)
parser.add_argument('--port', help="port", type=int, default=80)
args = parser.parse_args()


def badump(stop, service_name):
    while not stop.is_set():
        req = request.Request('http://registry:5000',
                              data=json.dumps({"service_name": service_name, "status": "UP"})
                              .encode("utf-8"),
                              headers={"Content-Type": "application/json"})
        res = request.urlopen(req)
        stop.wait(random.randint(8, 12))


def cleanup():
    stop.set()


stop = Event()
app.logger.debug("starting service")
hearthbeat = Thread(target=badump, args=[stop, args.name])
hearthbeat.start()

# cleanup threads on exit
atexit.register(cleanup)

app.run(host="0.0.0.0", port=args.port)

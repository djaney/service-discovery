#!/usr/bin/env python3
from flask import Flask
import argparse
from threading import Thread, Event
from urllib import request, error
import json
import atexit

app = Flask(__name__)


@app.route('/healthcheck')
def healthcheck():
    return '', 200


parser = argparse.ArgumentParser(description='Start Service')
parser.add_argument('name', help="service name", type=str)
parser.add_argument('--port', help="port", type=int, default=80)
parser.add_argument('--heartbeat', help="heartbeat interval", type=int, default=10)
parser.add_argument('--depends', '-d', help="depends on", type=str, action='append')
args = parser.parse_args()


def badump(stop, service_name, depends_on, heartbeat):
    if depends_on is None:
        depends_on = []

    while not stop.is_set():
        try:

            app.logger.debug("sent heartbeat")
            req = request.Request('http://registry:5000',
                                  data=json.dumps(
                                      {"service_name": service_name, "status": "UP"})
                                  .encode("utf-8"),
                                  headers={"Content-Type": "application/json"},
                                  method="PUT")
            request.urlopen(req)

            if heartbeat == 0:
                break  # kill it

        except error.HTTPError as e:
            if e.code == 404:
                app.logger.debug("registering service")
                req = request.Request('http://registry:5000',
                                      data=json.dumps(
                                          {"service_name": service_name, "depends_on": depends_on})
                                      .encode("utf-8"),
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
                request.urlopen(req)

        except Exception as e:
            app.logger.debug(str(e))
        stop.wait(heartbeat)


def cleanup():
    stop.set()


stop = Event()
app.logger.debug("starting service")
hearthbeat = Thread(target=badump, args=[stop, args.name, args.depends, args.heartbeat])
hearthbeat.start()

# cleanup threads on exit
atexit.register(cleanup)

app.run(host="0.0.0.0", port=args.port, debug=0)

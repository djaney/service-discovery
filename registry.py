#!/usr/bin/env python3
from flask import Flask, jsonify, request

import atexit
import argparse
from werkzeug.exceptions import HTTPException

from core.service_manager import ServiceManager


class ValidationException(HTTPException):
    code = 400
    description = "Validation Error"


services = ServiceManager()


def get_services():
    return jsonify(services.get_all())


def get_service(service_name):
    service = services.get(service_name)
    if service is not None and len(service) > 0:
        return jsonify(service)
    else:
        return '', 404


def add_service():
    post_data = request.get_json()

    # default is IP of caller
    if 'host' not in post_data:
        post_data['host'] = request.remote_addr

    if 'port' not in post_data:
        post_data['port'] = 80

    if 'depends_on' not in post_data:
        post_data['depends_on'] = []

    if 'service_name' not in post_data:
        raise ValidationException(description="Invalid service_name")

    if 'status' not in post_data:
        raise ValidationException(description="Invalid status")

    services.add(post_data['service_name'], post_data['host'], post_data['port'], post_data['status'], depends_on=post_data['depends_on'])

    return '', 200

def cleanup():
    services.stop_heartbeat_checker()


def main(args):
    app = Flask(__name__)
    # routes
    app.add_url_rule('/', 'get_services', get_services, methods=['GET'])
    app.add_url_rule('/<service_name>', 'get_service', get_service, methods=['GET'])
    app.add_url_rule('/', 'add_service', add_service, methods=['POST'])

    # start heartbeat checking thread
    services.start_heartbeat_checker(args.heartbeat)

    # cleanup threads on exit
    atexit.register(cleanup)

    # run in all interfaces
    app.run(host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Service')
    parser.add_argument('--heartbeat', help="Heartbeat lifetime", type=int, default=0)
    parser.add_argument('--port', help="Service port", type=int, default=5000)
    main(parser.parse_args())

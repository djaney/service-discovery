#!/usr/bin/env python3
from flask import Flask, jsonify, request

import atexit
import argparse
from werkzeug.exceptions import HTTPException

from core.service_manager import ServiceManager
from core.dot import Dot


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


def get_service_details(service_name):
    service = services.get(service_name, fields=['depends_on', 'healthcheck'])
    if service is not None and len(service) > 0:
        for v in service.values():
            return jsonify(v)
    else:
        return '', 404


def graph():
    d = Dot(services)
    return d.print(), 200


def add_service():
    post_data = request.get_json()

    if 'depends_on' not in post_data:
        post_data['depends_on'] = []

    if 'service_name' not in post_data:
        raise ValidationException(description="Invalid service_name")

    services.add(post_data['service_name'], depends_on=post_data['depends_on'])

    return '', 200


def remove_service(service_name):
    services.remove(service_name)
    return '', 200


def heartbeat_service():
    post_data = request.get_json()
    # default is IP of caller
    if 'host' not in post_data:
        post_data['host'] = request.remote_addr

    if 'port' not in post_data:
        post_data['port'] = 80

    if 'service_name' not in post_data:
        raise ValidationException(description="Invalid service_name")

    if 'status' not in post_data:
        raise ValidationException(description="Invalid status")

    if services.heartbeat(post_data['service_name'], post_data['host'], post_data['port'], post_data['status']):
        return '', 200
    else:
        return '', 404


def cleanup():
    services.stop_heartbeat_checker()


def main(args):
    app = Flask(__name__)
    # routes
    app.add_url_rule('/', 'get_services', get_services, methods=['GET'])
    app.add_url_rule('/graph', 'graph', graph, methods=['GET'])
    app.add_url_rule('/<service_name>', 'get_service', get_service, methods=['GET'])
    app.add_url_rule('/<service_name>/details', 'get_service_details', get_service_details, methods=['GET'])
    app.add_url_rule('/', 'add_service', add_service, methods=['POST'])
    app.add_url_rule('/', 'heartbeat_service', heartbeat_service, methods=['PUT'])
    app.add_url_rule('/<service_name>', 'remove_service', remove_service, methods=['DELETE'])

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

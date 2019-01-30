#!/usr/bin/env python3
from flask import Flask, jsonify, request
from threading import Thread, Event
from time import time, sleep
import atexit
import argparse
import math
from werkzeug.exceptions import HTTPException


class MortalThread(Thread):
    def __init__(self, sleep_interval=1, **kwargs):
        super().__init__(**kwargs)
        self._kill = Event()
        self._interval = sleep_interval

    def run(self):
        while True:
            if self._target:
                self._target(*self._args, **self._kwargs)

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

    def kill(self):
        self._kill.set()


class ValidationException(HTTPException):
    code = 400
    description = "Validation Error"


class Services:
    __heartbeat_lifetime = 0
    __services = {}
    __heartbeat_checker_thread = None

    def get_all(self):
        """
        Return all services
        :return: Services
        """
        return list(self.__services.keys())

    def get(self, service_name):
        """
        Return one services
        :return: Services
        """
        if service_name in self.__services:
            return self.__services[service_name]
        else:
            return None

    def add(self, service_name, host, port):
        """
        Register a service
        :param service_name:
        :param host:
        :param port:
        """
        if service_name not in self.__services.keys():
            self.__services[service_name] = {}
        self.__services[service_name]['{}:{}'.format(host, port)] = {'lhb': time()}

    def start_heartbeat_checker(self, lifetime):
        """
        start checking if services are still alive
        """
        self.__heartbeat_lifetime = lifetime
        if self.__heartbeat_lifetime > 0:
            self.__heartbeat_checker_thread = MortalThread(target=self.__heartbeat_checker,
                                                           sleep_interval=math.ceil(self.__heartbeat_lifetime/2))
            self.__heartbeat_checker_thread.start()

    def stop_heartbeat_checker(self):
        """
        stop checking if services are still alive
        """
        if self.__heartbeat_checker_thread is not None:
            self.__heartbeat_checker_thread.kill()
            self.__heartbeat_checker_thread.join()

    def __heartbeat_checker(self):
        """
        Delete if last heartbeat is more than lifespan
        """
        for_delete = []
        for service_key, service in self.__services.items():
            for key, obj in service.items():
                if time() - obj['lhb'] > self.__heartbeat_lifetime:
                    for_delete.append((service_key, key))

        for sk, k in for_delete:
            del self.__services[sk][k]
            if len(self.__services[sk]) == 0:
                del self.__services[sk]


services = Services()


def get_services():
    return jsonify(services.get_all())


def get_service(service_name):
    service = services.get(service_name)
    if service is not None:
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

    if 'service_name' not in post_data:
        raise ValidationException(description="Invalid service_name")

    services.add(post_data['service_name'], post_data['host'], post_data['port'])

    return '', 200


def handle_bad_request(err):
    return jsonify({"message": err.description or err}), err.code


def cleanup():
    services.stop_heartbeat_checker()


def main(args):
    app = Flask(__name__)
    app.add_url_rule('/', 'get_services', get_services, methods=['GET'])
    app.add_url_rule('/<service_name>', 'get_service', get_service, methods=['GET'])
    app.add_url_rule('/', 'add_service', add_service, methods=['POST'])

    app.register_error_handler(HTTPException, handle_bad_request)

    services.start_heartbeat_checker(args.heartbeat)

    atexit.register(cleanup)

    app.run(host="0.0.0.0")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Service')
    parser.add_argument('--heartbeat', help="Heartbeat lifetime", type=int, default=0)
    main(parser.parse_args())

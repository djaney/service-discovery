import math
from time import time
from core.threads import MortalThread
from enum import Enum


class Status(Enum):
    UP = 0
    DOWN = 1
    STARTING = 2
    OUT_OF_SERVICE = 3
    UNKNOWN = 4

    def __str__(self):
        return self.name


class ServiceManager:
    __heartbeat_lifetime = 0
    __services = {}
    __heartbeat_checker_thread = None

    PARAM_STATUS = 'status'
    PARAM_DEPENDS = 'depends_on'
    PARAM_HEALTHCHECK = 'healthcheck'

    def get_all(self):
        """
        Return all services live
        :return: Services
        """
        return list(self.__services.keys())

    def get(self, service_name, fields=None):
        """
        Return one services
        :return: Services
        """

        if fields is None:
            fields = ['status']

        if service_name in self.__services:
            endpoints = {}
            for key, value in self.__services[service_name]['nodes'].items():
                endpoints[key] = {}
                for f in fields:
                    if f == self.PARAM_STATUS:
                        endpoints[key][f] = str(value.get(f))
                    else:
                        endpoints[key][f] = self.__services[service_name][f]

        else:
            return None

        return endpoints

    def add(self, service_name, depends_on=None):
        """
        Register a service
        :param depends_on:
        :param service_name:
        :param host:
        :param port:
        :param status:
        """

        if depends_on is None:
            depends_on = []

        if service_name not in self.__services.keys():
            self.__services[service_name] = {
                'nodes': {},
                'healthcheck': '/',
                'depends_on': depends_on
            }

    def remove(self, service_name):
        if service_name not in self.__services.keys():
            return False

        del self.__services[service_name]

        return True

    def heartbeat(self, service_name, host, port, status):
        """
        Register a service
        :param service_name:
        :param host:
        :param port:
        :param status:
        """
        if Status[status] not in list(Status):
            raise ValueError("Invalid Status")

        if service_name not in self.__services.keys():
            return False

        self.__services[service_name]['nodes']['{}:{}'.format(host, port)] = {
            'lhb': time(),
            self.PARAM_STATUS: Status[status]}
        return True

    def start_heartbeat_checker(self, lifetime):
        """
        start checking if services are still alive
        """
        self.__heartbeat_lifetime = lifetime
        if self.__heartbeat_lifetime > 0:
            self.__heartbeat_checker_thread = MortalThread(target=self.__heartbeat_checker,
                                                           sleep_interval=math.ceil(self.__heartbeat_lifetime / 2))
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
        for service_key, service in self.__services.items():
            for key, obj in service['nodes'].items():
                if time() - obj['lhb'] > self.__heartbeat_lifetime:
                    self.__services[service_key]['nodes'][key][self.PARAM_STATUS] = Status.OUT_OF_SERVICE

    def services(self):
        return self.__services

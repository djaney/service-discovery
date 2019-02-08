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

    def get_all(self):
        """
        Return all services live
        :return: Services
        """
        return list(self.__services.keys())

    def get(self, service_name):
        """
        Return one services
        :return: Services
        """
        if service_name in self.__services:
            endpoints = {}
            for key, value in self.__services[service_name].items():
                status = value.get(self.PARAM_STATUS)
                if status is Status.UP:
                    endpoints[key] = {'status': str(status)}
        else:
            return None

        return endpoints

    def add(self, service_name, host, port, status):
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
            self.__services[service_name] = {}
        self.__services[service_name]['{}:{}'.format(host, port)] = {'lhb': time(), self.PARAM_STATUS: Status[status], 'healthcheck': '/'}

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
            for key, obj in service.items():
                if time() - obj['lhb'] > self.__heartbeat_lifetime:
                    self.__services[service_key][key][self.PARAM_STATUS] = Status.OUT_OF_SERVICE

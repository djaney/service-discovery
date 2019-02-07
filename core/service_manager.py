import math
from time import time
from core.threads import MortalThread


class ServiceManager:
    __heartbeat_lifetime = 0
    __services = {}
    __heartbeat_checker_thread = None

    def get_all(self):
        """
        Return all services live
        :return: Services
        """
        return list(self.__services.keys())

    def get(self, service_name, only_alive=True):
        """
        Return one services
        :return: Services
        """
        if service_name in self.__services:
            endpoints = {}
            for key, value in self.__services[service_name].items():
                if value.get('alive'):
                    endpoints[key] = value
        else:
            return None



        return endpoints

    def add(self, service_name, host, port):
        """
        Register a service
        :param service_name:
        :param host:
        :param port:
        """
        if service_name not in self.__services.keys():
            self.__services[service_name] = {}
        self.__services[service_name]['{}:{}'.format(host, port)] = {'lhb': time(), 'alive': True}

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
        for_delete = []
        for service_key, service in self.__services.items():
            for key, obj in service.items():
                if time() - obj['lhb'] > self.__heartbeat_lifetime:
                    for_delete.append((service_key, key))

        for sk, k in for_delete:
            del self.__services[sk][k]
            if len(self.__services[sk]) == 0:
                del self.__services[sk]

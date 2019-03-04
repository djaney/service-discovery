#!/usr/bin/env python3

import unittest
from urllib import request
import json


def json_post(url, data):
    req = request.Request(url,
                          data=json.dumps(data).encode("utf-8"),
                          headers={"Content-Type": "application/json"})
    res = request.urlopen(req)
    res_str = res.read().decode('utf-8')
    if res_str:
        data = json.loads(res_str)
        return data, res.status,
    else:
        return None, res.status


def json_get(url):
    req = request.Request(url, headers={"Content-Type": "application/json"})
    res = request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    return data, res.status


class TestRegistry(unittest.TestCase):
    def test_registry(self):
        res, status = json_post('http://registry:5000', {"service_name": "test", "status": "UP", "host": "sample"})
        self.assertEqual(200, status)

        res, status = json_get('http://registry:5000/test')

        self.assertEqual('UP', res['sample:80']['status'])
        self.assertEqual(200, status)

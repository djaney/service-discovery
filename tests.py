#!/usr/bin/env python3

import unittest
from urllib import request
import json


def json_post(url, data):
    req = request.Request(url,
                          data=json.dumps(data).encode("utf-8"),
                          headers={"Content-Type": "application/json"})
    res = request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    return data, 0


def json_get(url):
    req = request.Request(url, headers={"Content-Type": "application/json"})
    res = request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    return data, res.status


class TestRegistry(unittest.TestCase):
    def test_registry(self):
        res, status = json_post('http://registry:5000', {"service_name": "test", "status": "UP"})
        # self.assertEqual(200, status)

        # res, status = json_get('http://registry:5000/test')
        # print(res)
        # self.assertEqual(200, status)

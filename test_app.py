import pytest
from registry import get_app
import json
from argparse import Namespace

@pytest.fixture
def client():
    ns = Namespace(port=5000, heartbeat=0)
    app = get_app(ns)
    return app.test_client()


def test_register(client):
    rv = client.post('/', data=json.dumps({
        "service_name": "test",
        "status": "UP"
    }), content_type="application/json")

    assert 200 == rv.status_code


def test_heartbeat(client):
    rv = client.put('/', data=json.dumps({
        "service_name": "test",
        "status": "UP",
        "host": "sample"
    }), content_type="application/json")

    assert 200 == rv.status_code


def test_get_service(client):
    rv = client.get('/test')

    response = json.loads(rv.data.decode('utf-8'))

    assert 'UP' == response['sample:80']['status']

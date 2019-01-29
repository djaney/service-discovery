# Simple Service Discovery

## Endpoints

### Register service `POST /`
Sample request:
```json
    {"service_name":"test-service-0.0.1", "host":  "somewhere.com", "port":  8080}
```
only service name is required

* Call to register service.
* can also be called to for heartbeat
* Status `200` on success
* Status `400` on error
### Get all registered service `GET /`
Returns array of service names
### Get all endpoints of a particular service `GET /<service_name>`
Returns array of endpoint objects `host:port`

## Starting server
1. `make image`
1. `make start`

## Implementing clients
1. client must register the service in intervals to keep it alive
1. call get endpoints to get list of endpoints
1. manually load balance between endpoints

## build image as tar
`make build/image.tar`

## TODO
* Custom DNS
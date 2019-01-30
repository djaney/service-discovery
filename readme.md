# Simple Service Discovery

## Service Registry

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
Returns array of service names `[service_names...]`
### Get all endpoints of a particular service `GET /<service_name>`
Returns map of endpoint objects `{"host:port": {params...}}`

## DNS Server
Custom DNS Server requests the service registry. The `service_name` is the hostname and A record is returned.
If hostname does not exist in registry, request is forwarded to another DNS Server

## Starting server
Start registry at port 5000 and DNS at port 5053(tcp/udp)
1. `make build`
1. `make start`

## Implementing clients
1. client must register the service in intervals to keep it alive
1. call get endpoints to get list of endpoints
1. manually load balance between endpoints

## build image as tar
`make build/image.tar`

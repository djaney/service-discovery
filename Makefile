.PHONY: build run start stop sh

build:
	docker build -t service-discovery .

run:
	docker run -ti -p 5000:5000 service-discovery

start: stop
	docker run -d --rm -p 5000:5000 --name sd-registry service-discovery

stop:
	docker ps -f "ancestor=service-discovery" -q | xargs -r docker stop

sh:
	docker run --rm -it --entrypoint sh service-discovery
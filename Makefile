.PHONY: start stop test sim build build-test

start:
	docker-compose up -d registry dns

stop:
	docker-compose down

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up test

sim:
	FLASK_ENV=development docker-compose --compatibility -f docker-compose.yml -f docker-compose.sim.yml up

build:
	docker-compose build

build-test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml build
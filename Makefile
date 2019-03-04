.PHONY: start stop test sim

start:
	docker-compose up -d registry dns

stop:
	docker-compose down

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit test

sim:
	FLASK_ENV=development docker-compose --compatibility -f docker-compose.yml -f docker-compose.sim.yml up
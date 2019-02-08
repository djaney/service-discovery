.PHONY: start stop test

start:
	docker-compose up -d registry dns

stop:
	docker-compose down

test:
	docker-compose up --abort-on-container-exit test
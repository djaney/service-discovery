.PHONY: start stop test

start:
	docker-compose up -d registry dns

stop:
	docker-compose down

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit test
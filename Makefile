.PHONY: build start stop sh clean registry dns

build:
	docker build -t service-discovery .

registry:
	docker run -v $$(pwd):/app --rm -p 5000:5000 --name sd-registry service-discovery ./registry.py
dns:
	docker run -v $$(pwd):/app --rm -p 5053:5053 --name sd-dns service-discovery ./dns.py


start: stop
	docker run -d --rm -p 5000:5000 --name sd-registry service-discovery ./registry.py --heartbeat 30
	docker run -d --rm -p 5053:5053/udp -p 5053:5053/tcp --name sd-dns service-discovery ./dns.py --ttl 30

stop:
	docker ps -f "name=sd-registry" -q | xargs -r docker stop
	docker ps -f "name=sd-dns" -q | xargs -r docker stop

sh:
	docker run --rm -it service-discovery sh

build/image.tar: build
	mkdir -p $(dir $@)
	docker save service-discovery -o $@

clean:
	rm -rf build
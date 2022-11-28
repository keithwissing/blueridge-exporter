# Optionally include a compose makefile if needed
-include ../Makefile.compose

none:

build:
	docker build -t blueridge-exporter .

test-run:
	docker run --rm -it --env-file .env blueridge-exporter --test

stack-deploy:
	docker stack deploy -c docker-stack.yml blueridge-exporter

stack-ps:
	docker stack ps blueridge-exporter

stack-rm:
	docker stack rm blueridge-exporter

stack-services:
	docker stack services blueridge-exporter

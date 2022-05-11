# Optionally include a compose makefile if needed
-include ../Makefile.compose

none:

build:
	docker build -t blueridge-exporter .

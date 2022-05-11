include ../Makefile.compose

none:

build:
	docker build -t blueridge-exporter .

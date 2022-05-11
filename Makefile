ifneq ("$(wildcard ../Makefile.compose)","")
	include ../Makefile.compose
endif

none:

build:
	docker build -t blueridge-exporter .

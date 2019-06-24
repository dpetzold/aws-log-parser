VERSION := $(shell git rev-parse --short HEAD)
APP_NAME := aws-log-parser
DOCKER_REPO := dpetzold


.PHONY: build
build:
	docker build -t $(APP_NAME) .


.PHONY: tag
tag: build
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):$(VERSION)


.PHONY: push
push: tag
	docker push $(DOCKER_REPO)/$(APP_NAME):$(VERSION)


.PHONY: dist
dist:
	python3 setup.py sdist
	python3 -m twine upload  dist/*

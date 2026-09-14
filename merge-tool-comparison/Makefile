PYTHON ?= .venv/bin/python
MERGIRAF_VERSION ?= 0.17.0
SPORK_VERSION ?= 0.5.0
WEAVE_VERSION ?= 0.3.2
GJF_VERSION ?= 1.22.0

.PHONY: docker-build collect load-dataset load-dataset-force run evaluate report all test clean clean-all

docker-build:
	docker build --platform linux/amd64 -t merge-tools/git-merge-file docker/git-merge-file/
	docker build --platform linux/amd64 -t merge-tools/jdime docker/jdime/
	docker build --platform linux/amd64 -t merge-tools/spork -t merge-tools/spork:$(SPORK_VERSION) docker/spork/
	docker build --platform linux/amd64 -t merge-tools/mastery docker/mastery/
	docker build --platform linux/amd64 --build-arg MERGIRAF_VERSION=$(MERGIRAF_VERSION) -t merge-tools/mergiraf:$(MERGIRAF_VERSION) docker/mergiraf/
	docker build --platform linux/amd64 --build-arg WEAVE_VERSION=$(WEAVE_VERSION) -t merge-tools/weave:$(WEAVE_VERSION) docker/weave/
	docker build --build-arg GJF_VERSION=$(GJF_VERSION) -t merge-tools/google-java-format:$(GJF_VERSION) docker/google-java-format/

collect:
	$(PYTHON) -m src.cli collect

load-dataset:
	$(PYTHON) -m src.cli load-dataset

load-dataset-force:
	$(PYTHON) -m src.cli load-dataset --force

run:
	$(PYTHON) -m src.cli run

evaluate:
	$(PYTHON) -m src.cli evaluate

report:
	$(PYTHON) -m src.cli report --format console

all:
	$(PYTHON) -m src.cli all

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	rm -rf data/results/*

clean-all:
	rm -rf data/results/* reports/*

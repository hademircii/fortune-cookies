SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
APP_NAME:=app
PYTHON:=python3

all: dependencies

venv:
	if [ ! -d $(ROOT_DIR)/env ]; then $(PYTHON) -m venv $(ROOT_DIR)/env; fi

dependencies: venv
	source $(ROOT_DIR)/env/bin/activate; yes w | pip install --upgrade pip && \
	pip install -r requirements.txt --no-cache-dir

clean:
	# Remove existing environment
	rm -rf $(ROOT_DIR)/env; \
	rm -rf $(ROOT_DIR)/*.pyc;
	rm -rf $(ROOT_DIR)/*.egg-info;
	rm -rf $(ROOT_DIR)/dist;

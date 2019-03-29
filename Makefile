APP_NAME="$(shell basename $(PWD))"
APP_VOLUME="$(shell pwd):/app"

# Help
.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

DOCKER_RUN_CMD=docker run -i -t --rm --name=$(APP_NAME) -v=$(APP_VOLUME) $(APP_NAME)

build: ## Build the container
	docker build -t $(APP_NAME) .

shell: ## Creates a bash inside the container
	$(DOCKER_RUN_CMD) bash

run-scrapper: ## Run Scrapper
	$(DOCKER_RUN_CMD) python scrapper/getsongs.py

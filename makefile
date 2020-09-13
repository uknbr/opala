# Change the default config with `make cnf="config_special.env" build`
cnf ?= config.env
include $(cnf)
export $(shell sed 's/=.*//' $(cnf))

.PHONY: help

help: ## Display help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[35m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

run: ## Run Python script
	python3 car.py -r $(CAR_REGION)

build: ## Build the container
	docker image build --force-rm --network host -t olx-$(APP_NAME):$(APP_VERSION) .

up: ## Run container based on `config.env`
	docker container run -dti --rm --env-file=./config.env --name=olx-$(APP_NAME) --network host olx-$(APP_NAME):$(APP_VERSION)

stop: ## Stop and remove a running container
	docker container stop olx-$(APP_NAME) 2>/dev/null ; docker container rm -f olx-$(APP_NAME) 2>/dev/null ; docker info >/dev/null 2>&1

status: ## Check status of container
	docker container ls -f name=olx-$(APP_NAME)

sh: ## Access running container
	docker exec -ti olx-$(APP_NAME) sh

log: ## Follow the logs
	docker logs -f olx-$(APP_NAME)

restart: stop build up status ## Alias to stop, build, up and status

version: ## Output the current version
	@echo "olx-$(APP_NAME):$(APP_VERSION)"

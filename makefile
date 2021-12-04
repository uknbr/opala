# Change the default config with: make cnf="custom.env" status
cnf ?= config.env
include $(cnf)
export $(shell sed 's/=.*//' $(cnf))

.PHONY: help

help: ## Display help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[35m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

image: ## Build the container
	docker image build --force-rm --network host -t $(APP_IMAGE):$(APP_VERSION) .

start: ## Run container based on config file
	mkdir -p olx
	chmod 777 olx/
	docker container run -dti --env-file=./$(cnf) --name=$(APP_ID) --label id=$(APP_ID) --label app=olx --restart=always --network host -v $(shell pwd)/olx:$(DATA_MOUNT_PATH)/olx $(APP_IMAGE):$(APP_VERSION)

stop: ## Stop and remove a running container
	docker container rm -f $(APP_ID) 2>/dev/null || true

status: ## Check status of container
	docker container ls -f name=$(APP_ID)

sh: ## Access running container
	docker exec -ti $(APP_ID) sh

log: ## Follow the logs
	docker logs -f $(APP_ID)

restart: stop start status ## Alias to stop, start and status

dashboard: ## Start dashboard
	docker-compose dashboard/olx.yml up -d

version: ## Output the current version
	@echo "$(APP_IMAGE):$(APP_VERSION)"
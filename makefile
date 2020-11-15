# Change the default config with `make cnf="custom.env" build`
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
	docker image build --force-rm --network host -t $(APP_IMAGE):$(APP_VERSION) .

start: ## Run container based on `config.env`
	mkdir -p olx
	chmod 777 olx/
	docker container run -dti --env-file=./$(cnf) --name=$(CAR_MODEL) --restart=unless-stopped --network host -v $(shell pwd)/olx:$(DATA_MOUNT_PATH)/olx $(APP_IMAGE):$(APP_VERSION)

stop: ## Stop and remove a running container
	docker container rm -f $(CAR_MODEL) 2>/dev/null || true

status: ## Check status of container
	docker container ls -f name=$(CAR_MODEL)

sh: ## Access running container
	docker exec -ti $(CAR_MODEL) sh

log: ## Follow the logs
	docker logs -f $(CAR_MODEL)

restart: stop build start status ## Alias to stop, build, start and status

sync: ## Sync data to MySQL
	sqlite3mysql -f olx/db/car.db -d $(MYSQL_DATABASE) -h $(MYSQL_HOST) -P $(MYSQL_PORT) -u $(MYSQL_USER) -p $(MYSQL_PASS)

dashboard: ## Start dashboard
	cd dashboard
	docker-compose -f olx.yml up -d

version: ## Output the current version
	@echo "$(APP_IMAGE):$(APP_VERSION)"

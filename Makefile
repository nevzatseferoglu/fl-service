.PHONY: run kill docker-build docker-run docker-stop docker-rm test test-cov clean

# Define variables
APP_NAME=fl-service
PORT=8000
TEST_CMD=pytest tests/
COV_DIR=.coverage
HTML_COV_DIR=htmlcov/
DOCKER_IMAGE_NAME=fl-service
DOCKER_CONTAINER_NAME=fl-service

# FastAPI
START_DIR = app
START_FASTAPI_SOURCE = main
VAR_NAME = app


# Run the application locally
run:
	uvicorn ${START_DIR}.${START_FASTAPI_SOURCE}:${VAR_NAME} --reload --port ${PORT}

kill:
	ps aux | grep uvicorn | grep -v grep | awk '{print $$2}' | xargs kill -SIGINT

# Run the application with Docker
docker-build:
	docker build -t ${DOCKER_IMAGE_NAME} .

docker-run:
	docker run -d -p ${PORT}:${PORT} --name ${DOCKER_CONTAINER_NAME} ${DOCKER_IMAGE_NAME}

docker-stop:
	docker stop ${DOCKER_CONTAINER_NAME}

docker-rm:
	docker rm ${DOCKER_CONTAINER_NAME}

# Run the tests
test:
	${TEST_CMD}

# Run the tests with code coverage
test-cov:
	pytest --cov-report term-missing --cov=${APP_NAME} tests/
	coverage html -d ${HTML_COV_DIR} --omit="${APP_NAME}/__init__.py"

# Remove the code coverage files
clean:
	rm -rf .pytest_cache .coverage htmlcov

# Print help message
help:
	@echo "Available commands:"
	@echo " run          Run the application locally"
	@echo " kill         Kill the application which is running in the background"
# @echo " docker-build Build the Docker image"
# @echo " docker-run   Run the application with Docker"
# @echo " docker-stop  Stop the Docker container"
# @echo " docker-rm    Remove the Docker container"
# @echo " test         Run the tests"
# @echo " test-cov     Run the tests with code coverage"
	@echo " clean        Remove code coverage files"
	@echo " help         Print this help message"
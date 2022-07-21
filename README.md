# dais-dlq-handler-service

DAIS DLQ Handler Service (DDHS) is a Python/Flask project written in Python 3 with the goal of handling messages that land in the DLQ.

## Development environment setup

### Create .env file

Create an .env file by copying the existing env.example file from the repository.

### Run development environment

HDHS is intended to be executed in a Docker container, so it has its own Docker Image, which is defined within this repository in a Dockerfile.

To run an DDHS development container on the local machine, there are two supported options: do it using docker-compose-dev.yml file available in the repository, or using Docker commands.

By using docker-compose-dev.yml, docker-compose will also bring up two ActiveMQ development containers. If you want to use remote MQ instances, all you have to do is to update the corresponding MQ environment variables in the .env file to access the desired MQ instances.

#### Run using docker-compose

Note that for this option docker-compose must be installed.

Execute docker-compose up command:
````
docker-compose -f docker-compose-dev.yml up
````

#### Run using Docker commands

Note that this option will only run an DDHS container, without ActiveMQ containers.

First, build DDHS Docker image:
````
docker build --tag hdhs .
````

Then, execute Docker run command:
````
docker run -p 10580:5000 -v "$(pwd)"/app/:/home/hdhsuser/app hdhs
````

Remember to add the above run command volume mapping to allow automatic updating of code changes in the running container.

## Test environment setup

### Create integration .env file

A .test.env file must be created inside /test/integration by copying the existing test.env.example file which can be found in the same folder.

### Run test environment

Similar to the development environment, for running a local test environment there is a docker-compose-test.yml file, which contains a test runner container and an ActiveMQ container (for integration tests).

Before running tests locally, the environment must be up and running:
````
docker-compose -f docker-compose-test.yml up
````

### Running tests

Once the test environment is up and running, you can run the tests by executing pytest within the test runner container.

Running all tests:
````
docker exec -it test_runner pytest test
````

Running unit tests:
````
docker exec -it test_runner pytest test/unit
````

Running integration tests:
````
docker exec -it test_runner pytest test/integration
````

If you want to use a remote test environment for integration testing, you will need to update the environment variables in the corresponding .test.env file to access the desired environment.

## Versioning

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

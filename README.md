# dockermirror
Docker mirroring for networks without internet connectivity

# CLI usage

    python3 -m dockermirror --help

# API usage
Create archive:

    curl -v -H 'Content-Type: application/json' -XPOST -d '{"images": ["debian:latest", "python:3"]}' http://dockermirror:5000/api/v1/archive

Check url from location header for status:

    curl -v http://localhost:5000/api/v1/job/69e0eb21-7847-481a-96e6-2af2f773efa7

When the job has finished it is possible to check archive information from the status url location header as long as the file still exists:

    curl -v http://dockermirror:5000/api/v1/archive/_sYP7FfCCETSPeaNkQFXH69DLAPORf7ly2EhpGSQ1Ak.tar

# Run dockermirror command in docker container

    docker-compose run --rm dockermirror <dockermirror_args>

# Run API server in docker containers

    # Example bind mounted named volume
    docker volume create --opt type=none --opt o=bind --opt device=/path/to/archives --name archives
    docker-compose -f api-docker-compose.yml up

# Run tests

    docker-compose -f test-docker-compose.yml run --rm dockermirror-test

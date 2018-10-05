# dockermirror
Docker mirroring for networks without internet connectivity

# CLI usage

    python3 -m dockermirror --help

# API usage
Create archive:

    curl -H 'Content-Type: application/json' -XPOST -d '{"images": ["debian", "debian:jessie"]}' http://dockermirror:5000/api/v1/archive

View archive information:

    curl -XGET http://dockermirror:5000/api/v1/archive/_sYP7FfCCETSPeaNkQFXH69DLAPORf7ly2EhpGSQ1Ak.tar

# Run dockermirror command in docker container

    docker build -t dockermirror .
    docker run \
        --name dockermirror --rm \
        --mount 'type=bind,source=/tmp/dockermirror,target=/var/spool/dockermirror' \
        --mount 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock' \
        dockermirror \
        <args>

# Run API in a docker container

    docker build -f Dockermirror-api -t dockermirror-api .
    docker run \
        --name dockermirror-api --rm \
        -p 5000:5000 \
        --env FLASK_ENV=development \
        --mount 'type=bind,source=/tmp/dockermirror,target=/var/spool/dockermirror' \
        --mount 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock' \
        dockermirror-api

# dockermirror
Docker mirroring for networks without internet connectivity

# Docker container for API development

    docker build -t dockermirror .
    docker run \
	      --name dockermirror --rm \
	      -p 5000:5000 \
          --env FLASK_ENV=development \
	      --mount 'type=bind,source=/tmp/dockermirror,target=/var/spool/dockermirror' \
	      --mount 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock' \
	      dockermirror

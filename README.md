# docker-mirror
Docker mirroring for networks without internet connectivity

# Docker container for API development

    docker build -t docker-mirror .
    docker run \
	      --name docker-mirror --rm \
	      -p 5000:5000 \
          --env FLASK_ENV=development \
	      --mount 'type=bind,source=/tmp/docker-mirror,target=/var/spool/docker-mirror' \
	      --mount 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock' \
	      docker-mirror

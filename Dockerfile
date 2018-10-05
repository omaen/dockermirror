FROM docker

RUN apk add --no-cache python3

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY dockermirror/ dockermirror/

VOLUME /var/spool/dockermirror

ENTRYPOINT ["python3", "-m", "dockermirror"]

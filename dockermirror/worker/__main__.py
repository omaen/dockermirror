import redis
from rq import Worker, Queue, Connection
import flask

import dockermirror


REDIS_URL = 'redis://redis:6379'
QUEUES = ['default']


def main():
    conn = redis.from_url(REDIS_URL)

    with Connection(conn):
        worker = Worker(list(map(Queue, QUEUES)))
        worker.work()


if __name__ == '__main__':
    main()

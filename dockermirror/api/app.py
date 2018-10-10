import os
from pathlib import Path

import redis
from rq import Connection, Queue
from flask import Flask, jsonify, request, abort

from dockermirror import DockerImage, DockerArchive
from dockermirror.common import get_archive_name


app = Flask(__name__)
app.config.from_object('dockermirror.api.default_settings')

if 'DOCKERMIRROR_API_SETTINGS' in os.environ:
    app.config.from_envvar('DOCKERMIRROR_API_SETTINGS')

conn = redis.from_url(app.config['REDIS_URL'])


def create_archive(archive, images):
    """
    Wrapper for archive.save() used for redis queue, as instance methods
    is not supported as the function argument in rq.Queue.enqueue as pickle
    fails

    """
    archive.save(images, remove=False)
    return archive.name


@app.route('/')
def index():
    return "Dockermirror API"

@app.route('/api/v1/archive', methods=['POST'])
def add_save_task():
    if not request.json or 'images' not in request.json:
        abort(400)

    if not isinstance(request.json['images'], list):
        abort(400)

    filename = get_archive_name(request.json['images'])
    archive_path = Path(app.config['OUTPUT_DIR']).joinpath(filename)
    archive = DockerArchive(archive_path)
    images = [DockerImage(i) for i in request.json['images']]

    with Connection(conn):
        q = Queue('default')
        job = q.enqueue(create_archive, archive, images,
                        timeout='1h', ttl='24h', result_ttl='30d')

    response = {
        'job_id': job.get_id(),
        'images': [i.name for i in images],
    }
    headers = {
        'Location': '/api/v1/job/%s' % job.get_id()
    }

    return jsonify(response), 202, headers

@app.route('/api/v1/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    with Connection(conn):
        q = Queue('default')
        job = q.fetch_job(job_id)

        if not job:
            abort(400)

        if job.is_failed:
            status = {
                'status': job.get_status(),
                'error': job.exc_info.splitlines()[-1]
            }
            return jsonify(status), 200
        elif job.is_finished:
            headers = {
                'Location': '/api/v1/archive/%s' % job.result
            }
            status = {
                'status': job.get_status(),
                'result': 'Successfully created %s' % job.result
            }
            return jsonify(status), 303, headers
        else:
            status = {
                'status': job.get_status()
            }
            return jsonify(status), 202

@app.route('/api/v1/archive/<name>', methods=['GET'])
def get_archive_info(name):
    archive_path = Path(app.config['OUTPUT_DIR']).joinpath(name)
    archive = DockerArchive(archive_path)

    try:
        response = {
            "images": [i.name for i in archive.images],
            "archive": archive.name,
            "size": archive.stat().st_size
        }
    except FileNotFoundError:
        abort(404)

    return jsonify(response), 200

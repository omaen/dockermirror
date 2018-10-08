import os
from pathlib import Path

from flask import Flask, jsonify, request, abort

from ..lib import DockerImage, DockerArchive
from ..common import get_archive_name


app = Flask(__name__)
app.config.from_object('dockermirror.api.default_settings')

if 'DOCKER_MIRROR_API_SETTINGS' in os.environ:
    app.config.from_envvar('DOCKER_MIRROR_API_SETTINGS')


@app.route('/')
def index():
    return "Dockermirror API"

@app.route('/api/v1/archive', methods=['POST'])
def add_image():
    if not request.json or 'images' not in request.json:
        abort(400)

    if not isinstance(request.json['images'], list):
        abort(400)

    filename = get_archive_name(request.json['images'])
    archive_path = Path(app.config['OUTPUT_DIR']).joinpath(filename)
    archive = DockerArchive(archive_path)

    images = [DockerImage(i) for i in request.json['images']]
    archive.save(images, remove=False)

    response = {
        "images": [i.name for i in archive.images],
        "archive": archive.name,
        "size": archive.stat().st_size
    }

    return jsonify(response), 201

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

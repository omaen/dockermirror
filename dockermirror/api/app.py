from flask import Flask, jsonify, request, abort
import os
from pathlib import Path

from dockermirror import DockerImage, DockerArchive
from dockermirror.common import get_archive_name


app = Flask(__name__)
app.config.from_object('dockermirror.api.default_settings')

if 'DOCKER_MIRROR_API_SETTINGS' in os.environ:
    app.config.from_envvar('DOCKER_MIRROR_API_SETTINGS')

@app.route('/')
def index():
    return "Docker Mirror API"

@app.route('/api/v1/archive', methods=['POST'])
def add_image():
    if not request.json or 'images' not in request.json:
        abort(400)

    if not isinstance(request.json['images'], list):
        abort(400)

    #try:
    filename = get_archive_name(request.json['images'])
    archive_path = Path(app.config['OUTPUT_DIR']).joinpath(filename)
    archive = DockerArchive(archive_path)

    images = [DockerImage(i) for i in request.json['images']]
    archive.save(images, remove=False)
    #except subprocess.CalledProcessError as e:
    #    return jsonify({"error": "Could not mirror image '%s'" % request.json['image']}), 400

    response = {
        "images": request.json['images'],
        "archive": str(archive.filepath)
    }

    return jsonify(response), 201

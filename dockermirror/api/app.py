from flask import Flask, jsonify, request, abort
import subprocess
import os


app = Flask(__name__)
app.config.from_object('dockermirror.api.default_settings')

if 'DOCKER_MIRROR_API_SETTINGS' in os.environ:
    app.config.from_envvar('DOCKER_MIRROR_API_SETTINGS')

@app.route('/')
def index():
    return "Docker Mirror API"

@app.route('/api/v1/image', methods=['POST'])
def add_image():
    if not request.json or 'image' not in request.json:
        abort(400)

    cmd = [
        'python3',
        '-m', 'dockermirror',
        'save',
        '--output-dir', app.config['OUTPUT_DIR'],
        request.json['image']
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Could not mirror image '%s'" % request.json['image']}), 400

    response = {
        "image": request.json['image']
    }

    return jsonify(response), 201

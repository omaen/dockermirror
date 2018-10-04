import logging
import subprocess
import tarfile
import json


DOCKER = 'docker'
LOGGER = logging.getLogger(__name__)


class DockerImage(object):
    def __init__(self, name):
        self.name = name

    def pull(self):
        subprocess.run([DOCKER, 'pull', self.name], check=True)

    def push(self):
        subprocess.run([DOCKER, 'push', self.name], check=True)

    def tag(self, registry):
        tag = '%s/%s' % (registry, self.name)
        subprocess.run([DOCKER, 'tag', self.name, tag], check=True)
        return DockerImage(tag)

    def remove(self):
        LOGGER.debug('Removing docker image %s', self.name)
        subprocess.run([DOCKER, 'rmi', self.name], check=True)


class DockerArchive(object):
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.name = None
        self._manifest = None

    @property
    def manifest(self):
        if self._manifest is None:
            with tarfile.open(str(self.filepath)) as f:
                manifest_data = f.extractfile('manifest.json').read()
                self._manifest = json.loads(manifest_data.decode('utf-8'))
                LOGGER.debug(self._manifest)

        return self._manifest

    @property
    def images(self):
        for image in self.manifest:
            for tag in image['RepoTags']:
                yield DockerImage(tag)

    def remove(self):
        LOGGER.debug('Removing archive file %s', self.filepath)
        self.filepath.unlink()

    def _save(self, images):
        tmpfile = self.filepath.with_suffix('.tmp')
        cmd = [DOCKER, 'save', '--output', str(tmpfile)]
        cmd.extend([i.name for i in images])
        subprocess.run(cmd, check=True)
        tmpfile.rename(self.filepath)

    def save(self, images, remove=False):
        for image in images:
            image.pull()

        self._save(images)

        if remove:
            for image in images:
                image.remove()

    def _load(self):
        subprocess.run([DOCKER, 'load', '--input', str(self.filepath)], check=True)

    def load(self, registry=None, remove=False):
        self._load()

        if registry is not None:
            for image in self.images:
                tagged = image.tag(registry)
                tagged.push()
                tagged.remove()
                image.remove()

        if remove:
            self.remove()

import logging
import tarfile
import json
import subprocess

import docker


DOCKER = docker.from_env()
LOGGER = logging.getLogger(__name__)


class DockerImage:
    def __init__(self, name):
        self._name = None
        self._image = None
        self._registry = None
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def registry(self):
        if self._registry is None and '/' in self.name:
            first_part = self.name.split('/', 1)[0]
            if any(c in first_part for c in ['.', ':']):
                self._registry = first_part

        return self._registry

    def pull(self):
        LOGGER.debug('Pulling docker image %s', self.name)
        self._image = DOCKER.images.pull(self.name)

    def push(self):
        LOGGER.debug('Pushing docker image %s', self.name)
        DOCKER.images.push(self.name)

    def tag(self, repotag):
        if self._image is None:
            self._image = DOCKER.images.get(self.name)

        LOGGER.debug('Tagging docker image %s with tag %s', self.name, repotag)
        self._image.tag(repotag)
        return DockerImage(repotag)

    def remove(self):
        LOGGER.debug('Removing docker image %s', self.name)
        DOCKER.images.remove(self.name)


class DockerArchive:
    def __init__(self, filepath):
        self.filepath = filepath
        self._manifest = None
        self._name = None

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

    @property
    def name(self):
        if self._name is None:
            self._name = self.filepath.name

        return self._name

    def stat(self):
        return self.filepath.stat()

    def remove(self):
        LOGGER.debug('Removing archive file %s', self.filepath)
        self.filepath.unlink()

    def _save(self, images):
        """
        docker-py does not currently support saving multiple images at the same time
        so run docker directly in the meantime
        """
        tmpfile = self.filepath.with_suffix('.tmp')
        cmd = ['docker', 'save', '--output', str(tmpfile)]
        cmd.extend([i.name for i in images])
        LOGGER.debug('Saving images to archive file %s', self.filepath)
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
        with self.filepath.open('rb') as f:
            DOCKER.images.load(f)

    def load(self, registry=None, remove=False):
        self._load()

        if registry is not None:
            for image in self.images:
                if image.registry is None:
                    repotag = '%s/%s' % (registry, image.name)
                else:
                    repotag = image.name.replace(image.registry, registry, 1)

                tagged = image.tag(repotag)
                tagged.push()
                tagged.remove()
                image.remove()

        if remove:
            self.remove()

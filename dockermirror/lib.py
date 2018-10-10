import logging
import tarfile
import json
import subprocess
import hashlib
import base64

import docker


DOCKER = docker.from_env()
LOGGER = logging.getLogger(__name__)


class DockerMirror:
    @staticmethod
    def _get_filename(data):
        """
        Produce a length limited deterministic file system friendly name from
        variable input
        """
        h = hashlib.sha256()
        h.update(data)
        sha256 = h.digest()
        b64 = base64.urlsafe_b64encode(sha256)

        # Remove base64 padding (trailing '=' characters) as there is no need to
        # reverse the base64 operation later
        return b64.decode('utf-8').rstrip('=')

    def _get_archive_name(self, images):
        """
        Generate a deterministic archive filename based on image list
        """
        data = ''.join(sorted(i.name for i in images)).encode('utf-8')
        return '%s.tar' % self._get_filename(data)

    def save(self, output_dir, images, remove=False):
        """
        docker-py does not currently support saving multiple images at the same time
        so run docker directly in the meantime
        """
        filename = self._get_archive_name(images)
        filepath = output_dir.joinpath(filename)

        for image in images:
            image.pull()

        tmpfile = filepath.with_suffix('.tmp')
        cmd = ['docker', 'save', '--output', str(tmpfile)]
        cmd.extend([i.name for i in images])
        LOGGER.debug('Saving images to archive file %s', filepath)
        subprocess.run(cmd, check=True)
        tmpfile.rename(filepath)

        if remove:
            for image in images:
                image.remove()

        return DockerArchive(filepath)


class DockerImage:
    def __init__(self, name):
        self.name = name
        self._image = None
        self._registry = None

    @property
    def registry(self):
        if self._registry is None and '/' in self.name:
            first_part = self.name.split('/', 1)[0]
            if any(c in first_part for c in ['.', ':']):
                self._registry = first_part
        return self._registry

    @property
    def image(self):
        if self._image is None:
            self._image = DOCKER.images.get(self.name)
        return self._image

    def pull(self):
        LOGGER.debug('Pulling docker image %s', self.name)
        self._image = DOCKER.images.pull(self.name)

    def push(self):
        LOGGER.debug('Pushing docker image %s', self.name)
        DOCKER.images.push(self.name)

    def tag(self, repotag):
        LOGGER.debug('Tagging docker image %s with tag %s', self.name, repotag)
        self._image.tag(repotag)
        return DockerImage(repotag)

    def remove(self):
        LOGGER.debug('Removing docker image %s', self.name)
        DOCKER.images.remove(self.name)


class DockerArchive:
    def __init__(self, filepath):
        self.name = filepath.name
        self.filepath = filepath
        self._manifest = None
        self._images = []

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
        if not self._images:
            for image in self.manifest:
                for repotag in image['RepoTags']:
                    self._images.append(DockerImage(repotag))
        return self._images

    def stat(self):
        return self.filepath.stat()

    def remove(self):
        LOGGER.debug('Removing archive file %s', self.filepath)
        self.filepath.unlink()

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

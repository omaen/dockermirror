from dockermirror import DockerImage

class TestDockerMirror(object):
    def test_image_registry(self):
        name = 'registry.example.com:5000/username/image:latest'
        image = DockerImage(name)
        assert image.registry == 'registry.example.com:5000'

    def test_image_registry_no_port(self):
        name = 'registry.example.com/username/image:latest'
        image = DockerImage(name)
        assert image.registry == 'registry.example.com'

    def test_image_registry_group(self):
        name = 'username/image:latest'
        image = DockerImage(name)
        assert image.registry == None

    def test_image_registry_default(self):
        name = 'image:latest'
        image = DockerImage(name)
        assert image.registry == None

    def test_image_registry_notag(self):
        name = 'image'
        image = DockerImage(name)
        assert image.registry == None

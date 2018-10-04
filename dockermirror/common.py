import hashlib
import base64


def get_filename(data):
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

def get_archive_name(images):
    """
    Generate a deterministic archive filename based on image list
    """
    data = ''.join(sorted(images)).encode('utf-8')
    return '%s.tar' % get_filename(data)

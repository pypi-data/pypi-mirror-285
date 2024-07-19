from panos import panorama

from .utils import clean_url_host


class Panorama(panorama.Panorama):
    """
    Wrapper class for the Panorama class from pan-os-python library:
    https://pan-os-python.readthedocs.io/en/latest/readme.html#features

    Added features are:
    - hostname can be provided with and without the scheme
        - https://mydomain.com
        - mydomain.com
        - https://mydomain.com:443
      Are all valid
    """

    def __init__(
        self,
        hostname,
        api_username=None,
        api_password=None,
        api_key=None,
        port=None,
        *args,
        **kwargs,
    ):
        _, hostname, _port = clean_url_host(hostname)
        port = port or _port or 443
        return super().__init__(
            hostname, api_username, api_password, api_key, port, *args, **kwargs
        )

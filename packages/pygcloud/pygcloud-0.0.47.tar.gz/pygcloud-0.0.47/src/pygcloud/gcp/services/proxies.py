"""
HTTPS Proxy

@author: jldupont
"""
from pygcloud.models import GCPServiceUpdatable
from pygcloud.gcp.models import HTTPSProxy


class HTTPSProxyService(GCPServiceUpdatable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/target-https-proxies
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    SPEC_CLASS = HTTPSProxy
    PREFIX = ["compute", "target-https-proxies"]

    def __init__(self, name: str, ssl_certificate_name: str,
                 url_map_name: str):
        assert isinstance(ssl_certificate_name, str)
        assert isinstance(url_map_name, str)
        super().__init__(name=name, ns="https-proxy")
        self._ssl_certificate_name = ssl_certificate_name
        self._url_map_name = url_map_name

    def params_describe(self):
        return self.PREFIX + [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return self.PREFIX + [
            "create", self.name,
            "--ssl-certificates", self._ssl_certificate_name,
            "--url-map", self._url_map_name
        ]

    def params_update(self):
        return self.PREFIX + [
            "update", self.name,
            "--ssl-certificates", self._ssl_certificate_name,
            "--url-map", self._url_map_name
        ]

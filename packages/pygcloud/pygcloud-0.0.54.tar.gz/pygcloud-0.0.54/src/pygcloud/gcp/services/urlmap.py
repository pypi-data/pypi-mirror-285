"""
URL Maps

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable


class UrlMap(GCPServiceSingletonImmutable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/url-maps
    """
    LISTING_CAPABLE = True
    DEPENDS_ON_API = ["compute.googleapis.com",]
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    GROUP = ["compute", "url-maps"]


class UrlMapDefaultService(UrlMap):

    LISTING_CAPABLE = False

    def __init__(self, name: str, default_service_name: str):
        super().__init__(name=name, ns="urlmap")
        self._default_service_name = default_service_name

    def params_describe(self):
        return [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return [
            "create", self.name,
            "--global",
            "--default-service", self._default_service_name
        ]

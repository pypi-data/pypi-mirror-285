"""
Services

https://cloud.google.com/sdk/gcloud/reference/services

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable


class ServiceEnable(GCPServiceSingletonImmutable):
    """
    For enabling a service in a project
    """
    DEPENDS_ON_API = ["serviceusage.googleapis.com",]
    REQUIRES_DESCRIBE_BEFORE_CREATE = False
    GROUP = "services"

    def __init__(self, name: str):
        assert isinstance(name, str)
        super().__init__(name, ns="services")

    def params_create(self):
        return [
            "enable", self.name
        ]

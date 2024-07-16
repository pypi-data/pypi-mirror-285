"""
Compute Engine IP addresses

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable
from pygcloud.gcp.models import IPAddress


class ServicesAddress(GCPServiceSingletonImmutable):
    """
    For creating the IP address

    https://cloud.google.com/sdk/gcloud/reference/compute/addresses
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    SPEC_CLASS = IPAddress

    def __init__(self, name: str):
        super().__init__(name=name, ns="ip")

    def params_describe(self):
        return [
            "compute", "addresses", "describe", self.name,
            "--global", "--format", "json"
        ]

    def params_create(self):
        return [
            "compute", "addresses", "create", self.name,
            "--ip-version=IPv4", "--global",
            "--network-tier", "PREMIUM",
            "--format", "json"
        ]

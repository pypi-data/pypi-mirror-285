"""
Compute Engine Forwarding Rules

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable
from pygcloud.gcp.models import FwdRule


class FwdRuleHTTPSProxyService(GCPServiceSingletonImmutable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/forwarding-rules
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    PREFIX = ["compute", "forwarding-rules"]
    SPEC_CLASS = FwdRule

    def __init__(self, name: str, proxy_name: str, ip_address_name: str):
        assert isinstance(proxy_name, str)
        assert isinstance(ip_address_name, str)
        super().__init__(name=name, ns="fwd-rule")
        self._proxy_name = proxy_name
        self._ip_address_name = ip_address_name

    def params_describe(self):
        return self.PREFIX + [
            "describe", self.name,
            "--global",
            "--format", "json"
        ]

    def params_create(self):
        return self.PREFIX + [
            "create", self.name,
            "--global",
            "--target-https-proxy", self._proxy_name,
            "--address", self._ip_address_name,
            "--ports", "443"
        ]

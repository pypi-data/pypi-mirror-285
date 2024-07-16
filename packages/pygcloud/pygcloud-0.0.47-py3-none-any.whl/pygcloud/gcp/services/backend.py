"""
@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable, Params
from pygcloud.gcp.models import BackendServiceSpec


class BackendService(GCPServiceSingletonImmutable):
    """
    Backend services accessible external load balancers

    https://cloud.google.com/sdk/gcloud/reference/compute/backend-services
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    SPEC_CLASS = BackendServiceSpec

    def __init__(self, name: str, params_describe: Params,
                 params_create: Params):
        super().__init__(name=name, ns="be")
        self._params_describe = params_describe
        self._params_create = params_create

    def params_describe(self):
        return [
            "compute", "backend-services", "describe", self.name,
            "--format", "json"
        ] + self._params_describe

    def params_create(self):
        return [
            "compute", "backend-services", "create", self.name
        ] + self._params_create


class BackendServiceAddNeg(GCPServiceSingletonImmutable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/backend-services/add-backend
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = False

    def __init__(self, name: str, neg_name: str, region: str = None):
        super().__init__(name, "be")
        assert isinstance(region, str)
        assert isinstance(neg_name, str)
        self._neg_name = neg_name
        self._region = region

    def params_create(self):
        return [
            "compute", "backend-services", "add-backend", self.name,
            "--global",
            "--network-endpoint-group", self._neg_name,
            "--network-endpoint-group-region", self._region
        ]

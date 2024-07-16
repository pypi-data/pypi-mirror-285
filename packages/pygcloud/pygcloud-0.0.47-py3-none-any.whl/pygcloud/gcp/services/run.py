"""
@author: jldupont

# Labels

* The parameter `--labels` is an alias for `--update-labels`.
* When `--clear-labels` is also specified along with `--labels`,
  clearing takes precedence

# References

* [Cloud Run](https://cloud.google.com/run/docs/deploying)
"""
from pygcloud.models import GCPServiceRevisionBased, Params, \
    GCPServiceSingletonImmutable
from pygcloud.gcp.labels import LabelGenerator
from pygcloud.gcp.models import CloudRunRevisionSpec


class CloudRun(GCPServiceRevisionBased, LabelGenerator):

    SPEC_CLASS = CloudRunRevisionSpec

    def __init__(self, name: str, *params: Params, region: str = None):
        super().__init__(name=name, ns="run")
        assert isinstance(region, str)
        self.params = list(params)
        self.region = region

    def params_describe(self):
        return [
            "run", "services", "describe", self.name,
            "--region", self.region,
            "--format", "json"
        ]

    def params_create(self):
        """
        The common parameters such as project_id would normally
        be injected through the Deployer.
        """
        return [
            "beta", "run", "deploy", self.name,
            "--clear-labels",
            "--region", self.region,
        ] + self.params + self.generate_use_labels()


class CloudRunNeg(GCPServiceSingletonImmutable):
    """
    Cloud Run NEG

    https://cloud.google.com/sdk/gcloud/reference/beta/compute/network-endpoint-groups
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    PREFIX = ["beta", "compute", "network-endpoint-groups"]

    def __init__(self, name: str, *params: Params, region: str = None):
        assert isinstance(region, str)
        super().__init__(name, ns="crneg")
        self._region = region
        self._params = list(params) + ["--region", region]

    def params_describe(self):
        return self.PREFIX + [
            "describe",
            self.name,
            "--region", self._region
        ]

    def params_create(self):
        """
        In the params, typically:
        --cloud-run-url-mask=${URL_MASK}
        --cloud-run-service=${CLOUD_RUN_NAME}
        """
        return self.PREFIX + [
            "create",
            self.name,
            "network-endpoint-type", "serverless",
        ] + self._params

"""
echo "INFO: Creating certificate ${NAME}"
gcloud compute ssl-certificates create ${NAME} \
--project=${PROJECT_ID} \
--domains "${DOMAIN}"

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable
from pygcloud.gcp.models import SSLCertificate


class SSLCertificateService(GCPServiceSingletonImmutable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/ssl-certificates
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    SPEC_CLASS = SSLCertificate
    PREFIX = ["compute", "ssl-certificates"]

    def __init__(self, name: str, domain: str):
        assert isinstance(domain, str)
        super().__init__(name=name, ns="ssl")
        self._domain = domain

    def params_describe(self):
        return self.PREFIX + [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return self.PREFIX + [
            "create", self.name,
            "--domains", self.domain
        ]

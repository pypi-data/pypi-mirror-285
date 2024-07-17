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
    DEPENDS_ON_API = ["compute.googleapis.com",]
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    SPEC_CLASS = SSLCertificate
    GROUP = ["compute", "ssl-certificates"]

    def __init__(self, name: str, domain: str):
        assert isinstance(domain, str)
        super().__init__(name=name, ns="ssl")
        self._domain = domain

    def params_describe(self):
        return [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return [
            "create", self.name,
            "--domains", self.domain
        ]

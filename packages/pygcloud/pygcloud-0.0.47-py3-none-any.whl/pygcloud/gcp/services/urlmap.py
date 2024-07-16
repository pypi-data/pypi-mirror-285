"""
{
  "creationTimestamp": "2024-05-08T17:29:33.834-07:00",
  "defaultService": "https://www.googleapis.com/compute/v1/projects/PROJECT/
                        global/backendServices/backend-service",
  "fingerprint": "rUH-NY9dEXs=",
  "id": "922127737791030786",
  "kind": "compute#urlMap",
  "name": "urlmap-backend-service",
  "selfLink": "https://www.googleapis.com/compute/v1/projects/PROJECT/
                    global/urlMaps/urlmap-backend-service"
}

@author: jldupont
"""
from pygcloud.models import GCPServiceSingletonImmutable


class UrlMapDefaultService(GCPServiceSingletonImmutable):
    """
    https://cloud.google.com/sdk/gcloud/reference/beta/compute/url-maps
    """
    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    PREFIX = ["compute", "url-maps"]

    def __init__(self, name: str, default_service_name: str):
        super().__init__(name=name, ns="urlmap")
        self._default_service_name = default_service_name

    def params_describe(self):
        return self.PREFIX + [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return self.PREFIX + [
            "create", self.name,
            "--global",
            "--default-service", self._default_service_name
        ]

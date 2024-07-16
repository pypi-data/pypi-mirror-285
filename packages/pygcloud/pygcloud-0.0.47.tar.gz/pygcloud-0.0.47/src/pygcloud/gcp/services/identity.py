"""
Services Identity

@author: jldupont
"""
import logging
from pygcloud.models import GCPServiceSingletonImmutable, Result


class ServicesIdentityIAP(GCPServiceSingletonImmutable):
    """
    For creating the IAP service account

    https://cloud.google.com/sdk/gcloud/reference/beta/identity
    """

    @property
    def sa_email(self) -> str:
        """
        The address does not contain the usual 'serviceAccount' prefix
        """
        return self._service_account_email

    def params_create(self):
        return [
            "beta", "services", "identity", "create",
            "--service", "iap.googleapis.com",
            "--format", "json"
        ]

    def after_create(self, result: Result) -> Result:
        import json

        if not result.success:
            raise Exception("Could not create service account for IAP service")

        # It does not hurt: this transaction is idempotent anyways
        self.already_exists = False

        try:
            jsobj = json.loads(result.message)
            self._service_account_email = jsobj["email"]

        except Exception:
            raise Exception("Could not find service account email in:"
                            f" {result.message}")

        logging.debug("ServiceAccount for IAP successfully created"
                      " (if not already)")

        return result

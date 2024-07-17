"""
@author: jldupont
"""
from pygcloud.models import GCPServiceUpdatable, Params
from pygcloud.gcp.models import PubsubTopic


class PubsubTopic(GCPServiceUpdatable):
    """
    https://cloud.google.com/sdk/gcloud/reference/pubsub/
    """
    DEPENDS_ON_API = ["pubsub.googleapis.com",]
    SPEC_CLASS = PubsubTopic
    GROUP = ["pubsub", "topics"]

    def __init__(self, name: str, params_create: Params,
                 params_update: Params):
        assert isinstance(name, str)
        super().__init__(name, ns="pubsub-topic")
        self.params_create = list(params_create)
        self.params_update = list(params_update)

    def params_describe(self):
        return [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return [
            "create", self.name
        ] + self.params_create

    def params_update(self):
        return [
            "update", self.name
        ] + self.params_update

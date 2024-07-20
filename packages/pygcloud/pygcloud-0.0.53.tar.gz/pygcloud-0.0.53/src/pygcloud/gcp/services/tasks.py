"""
Cloud Tasks

https://cloud.google.com/sdk/gcloud/reference/tasks

@author: jldupont
"""
from pygcloud.models import Params, GCPServiceUpdatable
from pygcloud.gcp.models import TaskQueue


class TasksQueues(GCPServiceUpdatable):

    LISTING_CAPABLE = True
    DEPENDS_ON_API = ["cloudtasks.googleapis.com",]
    REQUIRES_UPDATE_AFTER_CREATE = False
    SPEC_CLASS = TaskQueue
    GROUP = ["tasks", "queues"]

    def __init__(self, name: str, params_create: Params = [],
                 params_update: Params = []):
        super().__init__(name=name, ns="queues")
        self._params_create = params_create
        self._params_update = params_update

    def params_describe(self):
        return [
            "describe", self.name,
            "--format", "json"
        ]

    def params_create(self):
        return [
            "create", self.name
        ] + self._params_create

    def params_update(self):
        return [
            "update", self.name
        ] + self._params_update

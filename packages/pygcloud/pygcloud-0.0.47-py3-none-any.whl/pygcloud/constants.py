"""@author: jldupont"""
from enum import Enum

__all__ = ["ServiceCategory"]


class ServiceCategory(Enum):
    INDETERMINATE = "indeterminate"
    SINGLETON_IMMUTABLE = "singleton_immutable"
    REVISION_BASED = "revision_based"
    UPDATABLE = "updateable"


class Instruction(Enum):
    ABORT_DEPLOY = "abort_deploy"
    ABORT_DEPLOY_ALL = "abort_deploy_all"

    def is_abort(self):
        return self == self.ABORT_DEPLOY or \
            self == self.ABORT_DEPLOY_ALL

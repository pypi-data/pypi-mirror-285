"""
Catalog facility for the supported GCP services

@author: jldupont
"""
from functools import cache
from pygcloud.gcp.services import *  # NOQA
from pygcloud.models import ServiceNode


@cache
def map():
    return {
        classe.__name__: classe
        for classe in ServiceNode.__all_classes__
    }


def lookup(class_name: str):
    return map().get(class_name, None)

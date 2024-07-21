"""
Helper commands

The default GCP project is retrieved from the environment
if possible either through key "_PROJECT_ID" or "PROJECT".

@author: jldupont
"""
import os

from typing import List
from pygcloud.core import GCloud
from pygcloud.models import Result
from pygcloud.gcp.models import ServiceDescription, ProjectDescription

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PROJECT_ID = os.environ.get("_PROJECT_ID", False) or \
             os.environ.get("PROJECT_ID", False) or \
             os.environ.get("PROJECT", False)


def cmd_retrieve_project_description() -> ProjectDescription:
    """
    Retrieve the project description
    """
    cmd = GCloud("projects", "describe", PROJECT_ID,
                 ..., "--format", "json",
                 cmd="gcloud", exit_on_error=True,
                 log_error=True)
    result: Result = cmd()
    return ProjectDescription.from_string(result.message)


def cmd_retrieve_enabled_services() -> List[ServiceDescription]:
    """
    Retrieve all enabled services in a project
    """
    cmd = GCloud("services", "list", ..., "--enabled",
                 "--project", PROJECT_ID,
                 "--format", "json",
                 cmd="gcloud", exit_on_error=True,
                 log_error=True)

    result: Result = cmd()

    liste: List[ServiceDescription] = \
        ServiceDescription.from_json_list(result.message)

    return liste

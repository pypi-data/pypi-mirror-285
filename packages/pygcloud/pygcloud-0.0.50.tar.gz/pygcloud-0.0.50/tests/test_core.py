"""
@author: jldupont
"""
import pytest
from pygcloud.core import CommandLine, GCloud


def test_cmd_line():
    cmd = CommandLine("echo")
    result = cmd.exec(["help"])
    assert result.success
    assert result.message == "help"


def test_cmd_not_found():
    cmd = CommandLine("--no-exec--")
    with pytest.raises(FileNotFoundError):
        cmd.exec(["no-exec"])


def test_cmd_line_exec_invalid():
    cmd = CommandLine("")
    with pytest.raises(PermissionError):
        cmd.exec(["no-exec"])


def test_cmd_directory():

    import tempfile
    dir = tempfile.gettempdir()
    cmd = CommandLine(dir)
    with pytest.raises(PermissionError):
        cmd.exec(["no-exec"])


def test_gcloud():
    gcloud = GCloud("head", ..., [("--last", "value")], cmd="echo")

    r = gcloud("head_after", "group", "command", [
        ("--param", "value")
    ])

    assert r.success
    assert r.message == \
        "head head_after group command --param value --last value", \
        r.message


def test_gcloud_flatten():

    gcloud = GCloud("head", ..., [("--tail", "value")], cmd="echo")

    r = gcloud("head_after", "group", "command", [
        [("--param", "value")]
    ])

    assert r.success
    assert r.message == \
        "head head_after group command --param value --tail value", \
        r.message


def _test_gcloud_service_does_not_exist():

    gcloud = GCloud()

    CTX = [
        ("--region", "northamerica-northeast1"),
        ("--format", "json")
    ]

    r = gcloud("run", "services", "describe", "whatever", CTX)

    """
    ERROR: (gcloud.run.services.describe) Cannot find service [whatever]
    """

    assert not r.success

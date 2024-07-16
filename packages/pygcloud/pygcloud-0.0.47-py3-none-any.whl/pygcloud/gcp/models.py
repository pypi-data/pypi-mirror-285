"""
Data models related to GCP services

@author: jldupont
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pygcloud.utils import JsonObject


class _base:

    @classmethod
    def parse_json(cls, json_str: str) -> dict:
        import json
        try:
            json_obj = json.loads(json_str)
        except Exception:
            raise ValueError(f"Cannot parse for JSON: {json_str}")

        return json_obj

    @classmethod
    def from_string(cls, json_str: str):
        """
        Create a dataclass from a JSON string
        Make sure to only include fields declare
        in the dataclass
        """
        obj = cls.parse_json(json_str)

        fields = cls.__annotations__

        sobj = {
            key: value for key, value in obj.items()
            if fields.get(key, None) is not None
        }
        return cls(**sobj)


@dataclass
class IAMBindings:

    members: List[str]
    role: str


@dataclass
class IAMBinding:
    """
    By default, if the 'email' does not
    contain a namespace prefix, it will be
    set to "serviceAccount"
    """

    ns: str
    email: str
    role: str

    def __post_init__(self):

        maybe_split = self.email.split(":")
        if len(maybe_split) == 2:
            self.ns = maybe_split[0]
            self.email = maybe_split[1]
        else:
            self.ns = "serviceAccount"

    @property
    def sa_email(self):
        return f"{self.ns}:{self.email}"


@dataclass
class IPAddress(_base):
    """
    Compute Engine IP address
    """
    name: str
    address: str
    addressType: str
    ipVersion: str


@dataclass
class CloudRunRevisionSpec:
    """
    Cloud Run Revision Specification (flattened)
    """
    name: str
    url: str
    labels: Dict

    @classmethod
    def from_string(cls, json_str: str):

        obj = JsonObject.from_string(json_str)

        d = {
            "url": obj["status.url"],
            "labels": obj["spec.template.metadata.labels"],
            "name": obj["metadata.name"],
        }

        return cls(**d)


@dataclass
class BackendGroup:
    balancingMode: str
    group: str
    capacityScaler: int


@dataclass
class BackendServiceSpec:

    name: str
    port: int
    portName: str
    protocol: str
    backend_groups: List[BackendGroup]

    @classmethod
    def from_string(cls, json_str: str):

        obj = JsonObject.from_string(json_str)

        raw_groups = obj["backends"]
        groups = []

        for group in raw_groups:
            group = BackendGroup(**group)
            groups.append(group)

        d = {
            "name": obj["name"],
            "port": obj["port"],
            "portName": obj["portName"],
            "protocol": obj["protocol"],
            "backend_groups": groups
        }

        return cls(**d)


@dataclass
class FwdRule(_base):
    """Attribute names come directly from gcloud describe"""

    name: str
    IPAddress: str
    IPProtocol: str
    loadBalancingScheme: str
    networkTier: str
    portRange: str
    target: str


@dataclass
class GCSBucket(_base):
    name: str
    location: str
    default_storage_class: str
    location_type: str
    metageneration: int
    public_access_prevention: str
    uniform_bucket_level_access: str


@dataclass
class SSLCertificate(_base):
    name: str
    type: str
    managed: Optional[dict] = field(default_factory=dict)


@dataclass
class HTTPSProxy(_base):
    name: str
    sslCertificates: Optional[list] = field(default_factory=list)
    urlMap: Optional[str] = field(default_factory="")


@dataclass
class SchedulerJob(_base):
    name: str
    retryConfig: dict
    schedule: str
    state: str
    timeZone: str
    location: str = "???"
    pubsubTarget: Optional[dict] = field(default_factory=dict)

    def __post_init__(self):
        parts = self.name.split("/")

        self.location = parts[3]
        self.name = parts[-1]


@dataclass
class PubsubTopic(_base):
    name: str

    def __post_init__(self):
        parts = self.name.split("/")
        self.name = parts[-1]

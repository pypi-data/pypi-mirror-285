"""
@author: jldupont
"""
from typing import List
from functools import cache
from pygcloud.models import Label, ServiceNode
from pygcloud.helpers import validate_name
from .utils import Codec


class LabelGenerator:
    """
    Mixin to generate labels for services

    NOTE: Cannot be used on its own
    """

    @classmethod
    @cache
    def generate_label(cls, target: ServiceNode) -> str:
        """
        Verifies if encoding is required for a label

        If encoding is required, verifies if a valid
        one can be generated

        A valid label must, encoded or not, must use
        less than 64 characters
        """
        def raise_if_too_long(value):
            assert isinstance(value, str)
            if len(value) > 63:
                raise ValueError("Label value is greater than 63 characters "
                                 f"for {target.__class__.name}")

        def raise_if_double_dash(value):
            assert isinstance(value, str)
            if '--' in value:
                raise ValueError("Invalid '--' in label component(s)  "
                                 f"{target.__class__.name}")

        raise_if_double_dash(target.ns)

        unencoded_name_is_valid = validate_name(target.name)

        if unencoded_name_is_valid and '--' not in target.name:
            label_value = cls.generate_one_label_value_unencoded(target)
            raise_if_too_long(label_value)
            return label_value

        # At this point, double - check is irrelevant
        # because these will get encoded, if any

        encoded_label_value = cls.generate_one_label_value_encoded(target)
        raise_if_too_long(encoded_label_value)

        return encoded_label_value

    @classmethod
    def generate_one_label_value_encoded(cls, service: ServiceNode) -> str:
        encoded_name = Codec.encode(service.name)
        return f"{service.ns}--{encoded_name}"

    @classmethod
    def generate_one_label_value_unencoded(cls, service: ServiceNode) -> str:
        return f"{service.ns}--{service.name}"

    def compute_use_entries(self) -> List[Label]:
        """
        TODO include validity check...
        """
        index = 0
        tuples = []
        for use in self.uses:
            tuples.append((f"pygcloud-use-{index}", f"{use.ns}--{use.name}"))
            index += 1

        return tuples

    def generate_string_from_labels(self, labels: List[Label]) -> str:
        return ",".join([f"{key}={value}" for key, value in labels])

    def generate_use_labels(self, param_prefix="--labels"):
        """
        Builds a list of labels for the service
        based on the "use" relationships.

        The management of labels (i.e. computing adds/removes)
        is not performed here.
        """
        if len(self.uses) == 0:
            return []

        labels: List[Label] = self.compute_use_entries()
        string_ = self.generate_string_from_labels(labels)

        return [
            f"{param_prefix}", string_
        ]

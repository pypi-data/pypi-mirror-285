"""
@author: jldupont
"""
from typing import List
from functools import cache
from pygcloud.utils import JsonObject
from .models import IAMBinding, IAMBindings


class _ProjectIAMBindings:
    """private methods"""

    def _get_bindings(self):

        self._bindings = [
            IAMBindings(members=item["members"], role=item["role"])
            for item in self.obj["bindings"]
        ]
        return self._bindings

    def _itemize(self, entry: IAMBindings) -> List[IAMBinding]:

        liste = entry.members
        role = entry.role

        return [
            IAMBinding(email=member, role=role, ns=...)
            for member in liste
        ]

    def _itemize_all(self) -> List[IAMBinding]:

        self._items: List[IAMBindings] = []

        for binding in self.bindings:
            items: List[IAMBinding] = self._itemize(binding)
            self._items.extend(items)

        return self._items


class ProjectIAMBindings(_ProjectIAMBindings):
    """
    Contains all the IAM bindings for a project

    By default, all namespace prefix are removed from the email address
    """
    def __init__(self, json_str: str):
        self.obj = JsonObject.from_string(json_str)
        self._bindings = None
        self._items = None

    @property
    @cache
    def items(self) -> List[IAMBinding]:
        return self._itemize_all()

    @property
    @cache
    def bindings(self) -> List[IAMBindings]:
        return self._get_bindings()

    @cache
    def find_bindings_by_member_email(self, email: str) -> List[IAMBinding]:
        """
        Retrieve all the bindings for a given member

        The namespace must be specified e.g. "serviceAccount:member@email"
        """

        items: List[IAMBinding] = self.items

        result: List[IAMBinding] = []
        item: IAMBinding

        for item in items:
            if item.email == email or item.sa_email == email:
                result.append(item)

        return result

    @cache
    def find_bindings_for_role(self, role: str) -> List[IAMBinding]:

        items: List[IAMBinding] = self.items

        result: List[IAMBinding] = []
        item: IAMBinding

        for item in items:
            if item.role == role:
                result.append(item)

        return result

    def check_for_target_binding(self, target_binding: IAMBinding) -> bool:

        bindings_for_member = \
            self.find_bindings_by_member_email(target_binding.email)

        for binding in bindings_for_member:
            if binding.role == target_binding.role:
                return True

        return False

"""
The database name "default" is special with Firestore: the default database
name is actually "(default)". So, in order to limit confusion, we treat the
name "default" and "(default)" the same. But for the rest of pygcloud to work
correctly, we strip the parenthesis from the name.

@author: jldupont
"""
from pygcloud.models import Params, GCPServiceSingletonImmutable
from pygcloud.helpers import remove_parenthesis


class FirestoreDbBase(GCPServiceSingletonImmutable):
    DEPENDS_ON_API = ["firestore.googleapis.com", "datastore.googleapis.com"]

    def __init__(self, db_name: str):
        name = remove_parenthesis(db_name)
        super().__init__(name=name, ns="fs-db")

    @property
    def db_name(self):
        if self.name == "default":
            return "(default)"
        return self.name


class FirestoreDatabase(FirestoreDbBase):

    REQUIRES_DESCRIBE_BEFORE_CREATE = True
    GROUP = ["firestore", "databases"]

    def __init__(self, name: str, params_create: Params = []):
        super().__init__(name)
        self._params_create = params_create

    def params_describe(self):
        return [
            "describe",
            "--database", self.db_name
        ]

    def params_create(self):
        return [
            "create",
            "--database", self.db_name
        ] + self._params_create


class FirestoreIndexComposite(GCPServiceSingletonImmutable):
    """
    Cannot describe an index unfortunately
    """
    DEPENDS_ON_API = ["firestore.googleapis.com", "datastore.googleapis.com"]
    GROUP = ["firestore", "indexes", "composite"]

    def __init__(self, db_name: str, params_create: Params = []):
        super().__init__(name=None, ns="fs-index")
        self.db_name = db_name
        self._params_create = params_create

    def params_create(self):
        return [
            "create",
            "--database", self.db_name
        ] + self._params_create

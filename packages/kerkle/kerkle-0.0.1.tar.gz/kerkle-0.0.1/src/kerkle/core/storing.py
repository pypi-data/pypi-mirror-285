# -*- encoding: utf-8 -*-
"""
kerkle.storing module

"""
from abc import ABC, abstractmethod
from typing import Union

import lmdb
from keri import core
from keri.db import dbing, subing
from kerkle.core.helping import PLACEHOLDER

BytesOrNone = Union[bytes, None]
DictOrNone = Union[dict, None]


class TreeMapStore(ABC):
    @abstractmethod
    def get_root(self) -> BytesOrNone:
        """
        Get the root for the tree.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def set_root(self, root: bytes, code=core.MtrDex.Blake3_256):
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def get_node(self, key: bytes) -> BytesOrNone:
        """
        Get a node for the given key.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def set_node(self, key: bytes, value: bytes) -> bool:
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def get_code(self) -> str:
        """
        Get the root for the tree.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def delete_node(self, key) -> bool:
        """
        Delete a node
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def save(self) -> bool:
        """
        Save to persistent datastore
        Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def load(self) -> bool:
        """
        Save to persistent datastore
        Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass


class LMDBTreeStore(dbing.LMDBer):
    TailDirPath = "keri/kerkle"
    AltTailDirPath = ".keri/kerkle"
    TempPrefix = "kerkle"

    def __init__(self, tid, name="test", headDirPath=None, reopen=True, **kwa):
        self.tid = tid
        self.nodes = None
        self.roots = None

        super(LMDBTreeStore, self).__init__(name=name, headDirPath=headDirPath, reopen=reopen, *kwa)

    def reopen(self, **kwa):
        """  Reopen database and initialize sub-dbs
        """
        super(LMDBTreeStore, self).reopen(**kwa)

        # Route definitions
        self.nodes = self.env.open_db(key=f"{self.tid}.nodes.".encode("utf-8"), dupsort=False)
        self.roots = subing.CesrSuber(db=self, subkey="roots.", klas=core.Matter)

    def getNodes(self) -> dict:
        """
        Get a node for the given key.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        nodes = dict()
        with self.env.begin(db=self.nodes, write=False, buffers=True) as txn:
            cursor = txn.cursor()
            if not cursor.set_range(b''):  # moves to val at key >= key, first if empty
                return nodes  # no values end of db

            for key, val in cursor.iternext():  # return key, val at cursor
                nodes[bytes(key)] = val

        return nodes

    def setNodes(self, nodes: dict) -> bool:
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        self.delTopVal(self.nodes)
        with self.env.begin(db=self.nodes, write=True, buffers=True) as txn:
            try:
                for key, val in nodes.items():
                    txn.put(key, val)
            except lmdb.BadValsizeError as ex:
                raise KeyError(f"Key: `{key}` is either empty, too big (for lmdb),"
                               " or wrong DUPFIXED size. ref) lmdb.BadValsizeError")
        return True

    def setRoot(self, root: core.Matter) -> bool:
        return self.roots.pin(keys=(self.tid,), val=root)

    def getRoot(self) -> core.Matter:
        return self.roots.get(keys=(self.tid,)) or core.Matter(raw=PLACEHOLDER, code=core.MtrDex.Blake3_256)


class TreeMemoryStore(TreeMapStore):
    root: core.Matter
    nodes: dict

    def __init__(self, db: Union[LMDBTreeStore, None], code=core.MtrDex.Blake3_256):
        self.root = core.Matter(raw=PLACEHOLDER, code=code)
        self.db = db
        self.nodes = {}

        if self.db and self.db.opened:
            self.load()

    def get_root(self) -> BytesOrNone:
        """
        Get the root for the tree.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        return self.root.raw

    def set_root(self, root: bytes, code=core.MtrDex.Blake3_256):
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        self.root = core.Matter(raw=root, code=code)

    def get_code(self) -> str:
        """
        Get the root for the tree.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        return self.root.code

    def get_node(self, key: bytes) -> BytesOrNone:
        """
        Get a node for the given key.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        return self.nodes.get(key, None)

    def set_node(self, key: bytes, value: bytes) -> bool:
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        self.nodes[key] = value
        return True

    def delete_node(self, key) -> bool:
        """
        Delete a node
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        if key not in self.nodes:
            return False
        del self.nodes[key]
        return True

    def save(self):
        self.db.setRoot(self.root)
        if self.db is not None:
            self.db.setNodes(self.nodes)

    def load(self):
        self.root = self.db.getRoot()
        if self.db is not None:
            self.nodes = self.db.getNodes()
        else:
            self.nodes = dict()

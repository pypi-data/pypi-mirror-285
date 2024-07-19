# -*- encoding: utf-8 -*-
"""
kerkle.proofing module

"""

from keri import core

from .helping import DEPTH, KEYSIZE, create_leaf, digest, LEAF, get_bit, create_node, RIGHT


class SparseMerkleProof:
    def __init__(self, root, value, sidenodes, non_membership_leafdata, siblingdata):
        self.root = root
        self.value = value
        self.sidenodes = sidenodes
        self.non_membership_leafdata = non_membership_leafdata
        self.sibling_data = siblingdata

    def sanity_check(self):
        if (
                len(self.sidenodes) > DEPTH
                or self.non_membership_leafdata is not None
                and len(self.non_membership_leafdata)
                != len(LEAF) + KEYSIZE + KEYSIZE
        ):
            return False

        for sn in self.sidenodes:
            if len(sn) != KEYSIZE:
                return False

        if self.sibling_data:
            sibhash = digest(self.sibling_data, code=self.root.code)
            if self.sidenodes and len(self.sidenodes) > 0:
                if self.sidenodes[0] != sibhash:
                    return False
        return True

    @property
    def pod(self):
        return dict(
            root=self.root.qb64,
            value=self.value.qb64,
            side_nodes=[core.Matter(raw=raw, code=self.root.code).qb64 for raw in self.sidenodes or []],
            non_membership_leafdata=[core.Matter(raw=raw, code=self.root.code).qb64 for raw in
                                     self.non_membership_leafdata or []],
            sibling_data=[core.Matter(raw=raw, code=self.root.code).qb64 for raw in self.sibling_data or []],
        )


def verify_proof(proof, root, saider):
    path = saider.raw

    if not proof.sanity_check():
        return False

    # if inverse:
    #     if not proof.non_membership_leafdata:
    #         current_hash = PLACEHOLDER
    #     else:
    #         actual_path, value_hash = parse_leaf(proof.non_membership_leafdata)
    #         if actual_path == path:
    #             return False
    #         current_hash, _current_data = create_leaf(actual_path, value_hash)
    # else:
    current_hash, _current_data = create_leaf(path)

    for i, node in enumerate(proof.sidenodes):
        if get_bit(len(proof.sidenodes) - 1 - i, path) == RIGHT:
            current_hash, _current_data = create_node(node, current_hash)
        else:
            current_hash, _current_data = create_node(current_hash, node)

    return current_hash == root

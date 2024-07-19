import random
import secrets

from keri import core
from keri.app import habbing
from keri.core import coring, MtrDex
from keri.help import helping
from keri.peer import exchanging
from kerkle.core import storing
from kerkle.core.treeing import SparseMerkleTree
from kerkle.core.proofing import verify_proof


def test_tree():
    with habbing.openHby(name="test", temp=True) as hby:
        hab = hby.makeHab(name="test", transferable=True)

        make_exns(hab)
        db = storing.LMDBTreeStore(tid="test", temo=True)
        store = storing.TreeMemoryStore(db=db)
        tree = SparseMerkleTree(store=store)

        saiders = []
        for (_,), exn in hby.db.exns.getItemIter():
            saider = coring.Saider(qb64b=exn.saidb)
            saiders.append(saider)
            tree.update(saider)

        assert len(saiders) == 500
        assert len(tree.root_as_bytes()) == 32
        root = core.Matter(raw=tree.root_as_bytes(), code=MtrDex.Blake3_256)

        for i in range(10):
            saider = random.choice(saiders)
            proof = tree.prove(saider)
            assert verify_proof(proof, root.raw, saider) is True
            assert tree.has(saider) is True

        assert proof.pod["root"] == root.qb64
        assert proof.pod["value"] == saider.qb64

        saider = coring.Saider(qb64b=b"EPmcEGTcz8-xNCOP6Bcg0ar57BVT6TumnJ4quwm-cnTH")
        proof = tree.prove(saider)
        assert not verify_proof(proof, root.raw, saider)
        assert not tree.has(saider)

        tree.store.save()
        db.close()

        db = storing.LMDBTreeStore(tid="test", demo=True)
        store2 = storing.TreeMemoryStore(db=db)
        tree2 = SparseMerkleTree(store=store)

        assert tree2.root == tree.root
        assert tree2.code == tree.code
        assert store2.nodes == store.nodes

        saider = random.choice(saiders)
        proof = tree2.prove(saider)
        assert verify_proof(proof, root.raw, saider) is True
        assert tree.has(saider) is True


def make_exns(hab):
    for i in range(500):
        raw = secrets.token_bytes(random.randint(30, 500))
        diger = coring.Diger(ser=raw, code=MtrDex.Blake3_256)

        exn, _ = exchanging.exchange(route="/essr/req",
                                     payload=dict(d=diger.qb64),
                                     sender=hab.pre,
                                     recipient="EM1GhHyd3Q7DDQ_U7h2JwwOVJNBfzIL4g1A-1qbx92Td",
                                     date=helping.nowIso8601())
        ims = hab.endorse(serder=exn, pipelined=False)
        hab.psr.parseOne(ims=bytes(ims))





from random import choice, randint
import string
from tempfile import TemporaryDirectory

import pytest

from ledger.immutable_store.stores.file_hash_store import FileHashStore
from hashlib import sha256


@pytest.fixture(scope="module")
def nodesLeaves():
    return [(randint(0, 1000000), randint(0, 255), h)
                                for h in generateHashes(10)], generateHashes(10),


def writtenFhs(tempdir, nodes, leaves):
    fhs = FileHashStore(tempdir)
    for leaf in leaves:
        fhs.writeLeaf(leaf)
    for node in nodes:
        fhs.writeNode(node)
    return fhs


def generateHashes(count=10):
    return [sha256(
        (choice(string.ascii_letters) * randint(i, 1000)).encode()
    ).digest() for i in range(count)]


def testSimpleReadWrite(nodesLeaves):
    with TemporaryDirectory() as tempdir:
        nodes, leaves = nodesLeaves
        fhs = FileHashStore(tempdir)

        for leaf in leaves:
            fhs.writeLeaf(leaf)
        for i, leaf in enumerate(leaves):
            assert leaf == fhs.getLeaf(i+1)

        for node in nodes:
            fhs.writeNode(node)
        for i, node in enumerate(nodes):
            assert node == fhs.getNode(i + 1)


def testIncorrectWrites():
    with TemporaryDirectory() as tempdir:
        fhs = FileHashStore(tempdir, leafSize=50, nodeSize=50)

        with pytest.raises(ValueError):
            fhs.writeLeaf(b"less than 50")
        with pytest.raises(ValueError):
            fhs.writeNode((8, 1, b"also less than 50"))

        with pytest.raises(ValueError):
            fhs.writeLeaf(b"more than 50" + b'1'*50)
        with pytest.raises(ValueError):
            fhs.writeNode((4, 1, b"also more than 50" + b'1'*50))


def testRandomAndRepeatedReads(nodesLeaves):
    with TemporaryDirectory() as tempdir:
        nodes, leaves = nodesLeaves
        fhs = writtenFhs(tempdir=tempdir, nodes=nodes, leaves=leaves)

        for i in range(10):
            idx = choice(range(len(leaves)))
            assert leaves[idx] == fhs.getLeaf(idx+1)

        for i in range(10):
            idx = choice(range(len(nodes)))
            assert nodes[idx] == fhs.getNode(idx + 1)

        idx = len(leaves) // 2
        # Even if same leaf is read more than once it should return the
        # same value. It checks for proper uses of `seek` method
        assert leaves[idx] == fhs.getLeaf(idx + 1)
        assert leaves[idx] == fhs.getLeaf(idx + 1)

        # Even after writing some data, the data at a previous index should not
        # change
        fhs.writeLeaf(leaves[-1])
        fhs.writeLeaf(leaves[0])
        assert leaves[idx] == fhs.getLeaf(idx + 1)
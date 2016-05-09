from ledger.stores.hash_store import HashStore


class MemoryHashStore(HashStore):
    def __init__(self):
        self._nodes = []
        self._leafs = []

    def writeLeaf(self, leafHash):
        self._leafs.append(leafHash)

    def writeNode(self, nodeHash):
        self._nodes.append(nodeHash)

    def readLeaf(self, pos):
        return self._leafs[pos - 1]

    def readNode(self, pos):
        return self._nodes[pos - 1]

    def readLeafs(self, startpos, endpos):
        return (n for n in self._leafs[startpos-1:endpos-1])

    def readNodes(self, startpos, endpos):
        return (n for n in self._nodes[startpos-1:endpos-1])

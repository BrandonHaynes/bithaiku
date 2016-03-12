import hashlib
import logging
from kademlia.network import Server
from kademlia.node import Node
import kademlia.utils


class BitHaikuDHT:
    log = logging.getLogger(__name__)

    def __init__(self, configuration):
        self.configuration = configuration
        self.server = Server()
        self.server.listen(configuration.ports.dht)
        self.server.bootstrap([(configuration.local_address, configuration.ports.dht)])

    def add(self, ip):
        self.log.error("Bootstrapping " + ip)
        self.server.bootstrap([(ip, self.configuration.ports.dht)])

    def find_owner(self, data):
        key = value = hashlib.sha256(data).hexdigest()
        self.server.set(key, value)

        digest = kademlia.utils.digest(hash)
        node = Node(digest)
        nearest = self.server.protocol.router.findNeighbors(node)
        return nearest[0].ip




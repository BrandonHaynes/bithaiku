import socket
import collections


class BitHaikuConfiguration:
    DEFAULT_INTERFACE = ''
    DEFAULT_MAX_SIZE = 65535
    DEFAULT_PORTS = {"server": 12000, "witness": 12001, "client": 12002, "dht": 12003}

    def __init__(self, ports=DEFAULT_PORTS, interface=DEFAULT_INTERFACE, max_size=DEFAULT_MAX_SIZE):
        self.ports = collections.namedtuple('Ports', 'server witness client dht')
        self.ports.server = ports['server']
        self.ports.client = ports['client']
        self.ports.witness = ports['witness']
        self.ports.dht = ports['dht']
        self.max_size = max_size
        self.interface = interface
        self.local_address = self._get_local_address()


    @staticmethod
    def _get_local_address():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            client.connect(("8.8.8.8", 80))
            return client.getsockname()[0]
        finally:
            client.close()
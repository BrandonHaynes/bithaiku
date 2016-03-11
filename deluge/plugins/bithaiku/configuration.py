import collections


class BitHaikuConfiguration:
    DEFAULT_INTERFACE = ''
    DEFAULT_MAX_SIZE = 65535
    DEFAULT_PORTS = {"server": 12000, "witness": 12001, "client": 12002}

    def __init__(self, ports=DEFAULT_PORTS, interface=DEFAULT_INTERFACE, max_size=DEFAULT_MAX_SIZE):
        self.ports = collections.namedtuple('Ports', 'server witness client')
        self.ports.server = ports['server']
        self.ports.client = ports['client']
        self.ports.witness = ports['witness']
        self.max_size = max_size
        self.interface = interface

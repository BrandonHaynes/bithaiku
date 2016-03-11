import SocketServer
import threading
import socket
import logging


class ServerTCPHandler(SocketServer.ThreadingMixIn, SocketServer.BaseRequestHandler):
    """
    Implements server functionality in the BitHaiku protocol.

    The server waits for a client to send it a haiku. It then 
    hashes the haiku and maps it to the DHT keyspace to find a witness.

    The server then transmits the address of the
    client owning the haiku and the haiku itself.
    """

    allow_reuse_address = True
    log = logging.getLogger(__name__)

    @classmethod
    def listen(cls, configuration):
        server = SocketServer.TCPServer((configuration.interface, configuration.ports.server), ServerTCPHandler)
        server.configuration = configuration
        server.terminate = lambda: (server.shutdown(), server.socket.close())
        threading.Thread(target=server.serve_forever).start()
        return server

    def handle(self):
        # Receive the data from the client
        data = self.request.recv(self.server.configuration.max_size).strip()
        self.log.error("Server: received {} from {}".format(data, self.client_address[0]))

        # Identify the address of the witness
        witness_hostname = self.select_witness(data)

        # Send haiku to the witness
        witness = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            witness.connect((witness_hostname, self.server.configuration.ports.witness))
            witness.sendall(data)
        finally:
            witness.close()

    @staticmethod
    def select_witness(haiku):
        # TODO Hash the haiku and use the DHT to obtain
        # the address for a witness.

        # Return the placeholder witness address
        return "localhost"

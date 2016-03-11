import SocketServer
import threading
import socket
import logging
import hashlib
import json


class WitnessTCPHandler(SocketServer.BaseRequestHandler):
    """
    Implements witness functionality in the BitHaiku protocol.

    The witness waits for a server to send it a haiku and the 
    address of the client who owns the haiku.

    It then hashes the haiku and sends the has to the client,
    demonstrating that it was received from the server.
    """

    allow_reuse_address = True
    log = logging.getLogger(__name__)

    @classmethod
    def listen(cls, configuration):
        server = SocketServer.TCPServer((configuration.interface, configuration.ports.witness), WitnessTCPHandler)
        server.terminate = lambda: (server.shutdown(), server.socket.close())
        server.configuration = configuration
        threading.Thread(target=server.serve_forever).start()
        return server

    def handle(self):
        # Receive the data from the server, which is the haiku
        data = self.request.recv(self.server.configuration.max_size).strip()
        message = json.loads(data)
        self.log.error("Witness: received {} from {}".format(data, self.client_address[0]))

        # Send hash of haiku to the known client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to client and send the hash of the haiku 
            client.connect((message['host'], self.server.configuration.ports.client))
            client.sendall(self.generate_client_response(message))
        finally:
            client.close()

    @staticmethod
    def generate_client_response(message):
        return json.dumps({'hash': hashlib.sha256(message['data']).hexdigest()})

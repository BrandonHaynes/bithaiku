import SocketServer
import socket
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

    def handle(self):
        # Recieve the data from the server, which is the haiku
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # Send back the same data
        self.request.sendall(self.data.upper())

        # Get the haiku and address from the JSON object
        message = json.loads(self.data)
        ClientHOST, ClientPORT = message['client_host'], message['client_port']        
        haiku = message['haiku']

        # Send hash of haiku to the known client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        try:
            # Connect to client and send the hash of the haiku 
            sock.connect((ClientHOST, ClientPORT))
            sock.sendall(hashlib.sha256(haiku).hexdigest())

            # Receive data from the server and shut down
            received = sock.recv(1024)
        finally:
            sock.close() 

if __name__ == "__main__":
    # TODO Generate witness addresses
    HOST, PORT = "localhost", 12002

    # Create the server
    server = SocketServer.TCPServer((HOST, PORT), WitnessTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

import SocketServer
import socket
import json

class ServerTCPHandler(SocketServer.BaseRequestHandler):
    """
    Implements server functionality in the bithaiku protocol.

    The server waits for a client to send it a haiku. It then 
    hashes the haiku and maps it to the DHT keyspace to find a witness.

    The server then transmits the address of the
    client owning the haiku and the haiku itself.
    """

    def handle(self):
        # Recieve the data from the client, which is the haiku
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # Acknowledge receipt of haiku
        self.request.sendall("> Thanks, I won't share that with anyone *wink*\n")

        # Create json object
        messsage = json.dumps(
                { 'client_host': 'localhost',
                  'client_port': '12002',
                  'haiku': 'furu ike ya\nkawazu tobikomu\nmizu no oto'
                 })

        # Identify the address of the witness
        WitnessHOST, WitnessPORT = self.select_witness(self.data)        

        # Send haiku to the witness
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect((WitnessHOST, WitnessPORT))
            sock.sendall(messsage)

            # Receive data from the server and shut down
            received = sock.recv(1024)
        finally:
            sock.close() 

    def select_witness(self, haiku):
        # TODO Hash the haiku and use the DHT to obtain
        # the address for a witness.

        # Return the placeholder witness address
        return ("localhost", 12002)
        


if __name__ == "__main__":
    # TODO Generate server addresses 
    HOST, PORT = "localhost", 12000

    # Create the server
    server = SocketServer.TCPServer((HOST, PORT), ServerTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

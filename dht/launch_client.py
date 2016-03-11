import SocketServer

class ClientTCPHandler(SocketServer.BaseRequestHandler):
    """
    This is a dummy listener for testing BitHaiku.
    It currently just listens for connections and prints out
    messages sent.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # send back the data
        self.request.sendall(self.data)

if __name__ == "__main__":
    HOST, PORT = "localhost", 12001

    server = SocketServer.TCPServer((HOST, PORT), ClientTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

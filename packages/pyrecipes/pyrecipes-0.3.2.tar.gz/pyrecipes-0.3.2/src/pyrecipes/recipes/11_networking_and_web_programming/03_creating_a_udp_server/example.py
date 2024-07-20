"""
You want to implement a server that communicates with clients using the UDP
internet protocol.
"""

from socketserver import UDPServer, BaseRequestHandler
import time


class TimeHandler(BaseRequestHandler):
    def handle(self):
        print("Got connection from", self.client_address)
        msg, sock = self.request
        resp = time.ctime()
        sock.sendto(resp.encode("ascii"), self.client_address)


def serve():
    serv = UDPServer(("", 20000), TimeHandler)
    serv.serve_forever()


def main():
    pass


if __name__ == "__main__":
    main()

"""
You want to implement a server that communicates with clients using the TCP internet protocol.
"""

from socketserver import (
    BaseRequestHandler,
    TCPServer,
    StreamRequestHandler,
    ThreadingTCPServer,
)
from socket import socket, AF_INET, SOCK_STREAM


class EchoHandler(BaseRequestHandler):
    def handle(self):
        print("Got connection from", self.client_address)
        while True:
            msg = self.request.recv(8192)
            if not msg:
                break
            self.request.send(msg)


class EchoStreamHandler(StreamRequestHandler):
    def handle(self):
        print("Got connection from", self.client_address)
        # self.rfile is a file-like object for reading
        for line in self.rfile:
            # self.wfile is a file-like object for writing
            self.wfile.write(line)


def serve_single_threaded(handler):
    serv = TCPServer(("", 20000), handler)
    serv.serve_forever()


def serve_multi_threaded(handler):
    serv = ThreadingTCPServer(("", 20000), handler)
    serv.serve_forever()


def test_server():
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("localhost", 20000))
    s.send(b"Hello")
    s.recv(8192)


def main():
    pass


if __name__ == "__main__":
    main()

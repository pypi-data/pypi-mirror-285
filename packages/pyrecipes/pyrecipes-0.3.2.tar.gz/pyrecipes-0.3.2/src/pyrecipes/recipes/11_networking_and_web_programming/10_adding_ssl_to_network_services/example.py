"""
You want to implement a network service involving sockets where servers
and clients authenticate themselves and encrpyt the transmitted data
using SSL.
"""

import ssl
from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from xmlrpc.server import SimpleXMLRPCServer


class SSLMixin:
    def __init__(
        self,
        *args,
        keyfile=None,
        certfile=None,
        ca_certs=None,
        cert_reqs=ssl.CERT_NONE,
        **kwargs,
    ):
        self._keyfile = keyfile
        self._certfile = certfile
        self._ca_certs = ca_certs
        self._cert_reqs = cert_reqs
        super().__init__(*args, **kwargs)

    def get_request(self):
        client, addr = super().get_request()
        client_ssl = ssl.wrap_socket(
            client,
            keyfile=self._keyfile,
            certfile=self._certfile,
            ca_certs=self._ca_certs,
            cert_reqs=self._cert_reqs,
            server_side=True,
        )
        return client_ssl, addr


class SSLSimpleXMLRPCServer(SSLMixin, SimpleXMLRPCServer):
    pass


class KeyValueServer:
    _rpc_methods_ = ["get", "set", "delete", "exists", "keys"]

    def __init__(self, *args, **kwargs):
        self._data = {}
        self._serv = SSLSimpleXMLRPCServer(*args, allow_none=True, **kwargs)
        for name in self._rpc_methods_:
            self._serv.register_function(getattr(self, name))

    def get(self, name):
        return self._data[name]

    def set(self, name, value):
        self._data[name] = value

    def delete(self, name):
        del self._data[name]

    def exists(self, name):
        return name in self._data

    def keys(self):
        return list(self._data)

    def serve_forever(self):
        self._serv.serve_forever()


KEYFILE = "server_key.pem"  # Private key of the server
CERTFILE = "server_cert.pem"  # Server certificate (given to client)


def echo_client(s):
    while True:
        data = s.recv(8192)
        if data == b"":
            break
        s.send(data)
    s.close()
    print("Connection closed")


def echo_server(address):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(address)
    s.listen(1)

    # Wrap with an SSL layer requiring client certs
    s_ssl = ssl.wrap_socket(s, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)
    # Wait for connections
    while True:
        try:
            c, a = s_ssl.accept()
            print("Got connection", c, a)
            echo_client(c)
        except Exception as e:
            print("{}: {}".format(e.__class__.__name__, e))


def test_client():
    echo_server(("", 20000))
    s = socket(AF_INET, SOCK_STREAM)

    # Wrap with an SSL layer and require the server to present its certificate
    ssl_s = ssl.wrap_socket(
        s,
        cert_reqs=ssl.CERT_REQUIRED,
        ca_certs="server_cert.pem",
    )

    ssl_s.connect(("localhost", 20000))

    # Communicate with the server
    ssl_s.send(b"Hello World!")
    resp = ssl_s.recv(8192)
    print("Got:", resp)

    # Done
    ssl_s.close()


def main():
    print(
        """
    Use the following commands to generate SSL certs:

    openssl req -new -x509 -days 365 -nodes -out server_cert.pem -keyout server_key.pem
    openssl req -new -x509 -days 365 -nodes -out client_cert.pem -keyout client_key.pem
        """
    )


if __name__ == "__main__":
    main()

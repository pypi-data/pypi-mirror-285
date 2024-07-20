"""
You want a simple way to authenticate the clients connecting to servers in
a distributed system, but don't need the complexity of something like SSL.
"""

import hmac
import os


def client_authenticate(connection, secret_key):
    """
    Authenticate client to a remote service.
    connection represents a network connection
    secret_key is a key known only to the slient/server.
    """
    message = connection.recv(32)
    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    connection.send(digest)


def server_authenticate(connection, secret_key):
    """
    Request client authentication.
    """
    message = os.urandom(32)
    connection.send(message)
    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    response = connection.recv(len(digest))
    return hmac.compare_digest(digest, response)


def main():
    pass


if __name__ == "__main__":
    main()

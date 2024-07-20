"""
You want to implement simple remote procedure call (RPC) on top of a message
passing layer, such as sockets, multiprocessing connections, or ZeroMQ.
"""

from multiprocessing.connection import Listener, Client
import pickle
from threading import Thread


class RPCHandler:
    def __init__(self):
        self._functions = {}

    def register_function(self, func):
        self._functions[func.__name__] = func

    def handle_connection(self, connection):
        try:
            while True:
                # Receive a message
                func_name, args, kwargs = pickle.loads(connection.recv())
                # Run the function
                try:
                    result = self._functions[func_name](*args, **kwargs)
                    connection.send(pickle.dumps(result))
                except Exception as e:
                    connection.send(pickle.dumps(e))
        except EOFError:
            pass


class RPCProxy:
    def __init__(self, connection):
        self._connection = connection

    def __getattr__(self, name):
        def do_rpc(*args, **kwargs):
            self._connection.send(pickle.dumps((name, args, kwargs)))
            result = pickle.loads(self._connection.recv())
            if isinstance(result, Exception):
                raise result
            return result

        return do_rpc


def rpc_server(handler, address, authkey):
    print(f"Starting RPC server on {address}")
    sock = Listener(address, authkey=authkey)
    while True:
        client = sock.accept()
        t = Thread(target=handler.handle_connection, args=(client,), daemon=True)
        t.start()


def add(x, y):
    return x + y


def sub(x, y):
    return x - y


def main():
    handler = RPCHandler()
    handler.register_function(add)
    handler.register_function(sub)
    t = Thread(
        target=rpc_server,
        args=(handler, ("", 17000), b"peekaboo"),
        daemon=True,
    )
    t.start()

    client = Client(("localhost", 17000), authkey=b"peekaboo")
    proxy = RPCProxy(client)
    print(proxy.add(2, 3))
    print(proxy.sub(3, 2))
    try:
        print(proxy.add([1, 2], 3))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

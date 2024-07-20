"""
You want an easy way to execute functions or methods in Python programs running on remote machines.
"""

from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy


class KeyValueServer:
    _rpc_methods = ["get", "set", "delete", "exists", "keys"]

    def __init__(self, address):
        self._data = {}
        self._serv = SimpleXMLRPCServer(address, allow_none=True)
        for name in self._rpc_methods:
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
        print(f"Serving on {self._serv.server_address}")
        self._serv.serve_forever()


def main():
    kvserv = KeyValueServer(("", 15000))
    t = Thread(target=kvserv.serve_forever, daemon=True)
    t.start()

    s = ServerProxy("http://localhost:15000", allow_none=True)
    s.set("foo", "bar")
    s.set("spam", [1, 2, 3])
    print(s.keys())
    print(s.get("foo"))
    print(s.get("spam"))
    print(s.exists("spam"))
    s.delete("spam")
    print(s.exists("spam"))


if __name__ == "__main__":
    main()

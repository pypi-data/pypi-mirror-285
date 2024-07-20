"""
You are running multiple instances of the Python interpreter, possible on
different machines, and you would like to exchange data between interpreters
using messages.
"""

from threading import Thread
from multiprocessing.connection import Listener, Client
import traceback


def echo_client(conn):
    try:
        while True:
            msg = conn.recv()
            conn.send(msg)
    except EOFError:
        print("Connection closed.")


def echo_server(address, authkey):
    print(f"Starting server on {address}")
    serv = Listener(address, authkey=authkey)
    while True:
        try:
            client = serv.accept()
            echo_client(client)
        except Exception:
            traceback.print_exc()


def main():
    t = Thread(target=echo_server, args=(("", 25000), b"peekaboo"), daemon=True)
    t.start()

    conn = Client(("localhost", 25000), authkey=b"peekaboo")
    for value in ("hello", 42, [1, 2, 3]):
        conn.send(value)
        received = conn.recv()
        print("received:", received)


if __name__ == "__main__":
    main()

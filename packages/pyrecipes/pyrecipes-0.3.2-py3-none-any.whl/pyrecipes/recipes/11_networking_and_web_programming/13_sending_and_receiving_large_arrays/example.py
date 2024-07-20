"""
You want to send and receive large arrays of contiguous data across a
network connection, making as few copies of the data as possible.
"""

from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import numpy as np


def send_from(arr, dest):
    view = memoryview(arr).cast("B")
    while len(view):
        nsent = dest.send(view)
        view = view[nsent:]


def recv_into(arr, source):
    view = memoryview(arr).cast("B")
    while len(view):
        nrecv = source.recv_into(view)
        view = view[nrecv:]


def server():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(("", 25000))
    s.listen(1)
    c, a = s.accept()
    a = np.arange(0.0, 500000.0)
    send_from(a, c)


def main():
    t = Thread(target=server, daemon=True)
    t.start()

    c = socket(AF_INET, SOCK_STREAM)
    c.connect(("localhost", 25000))
    arr = np.zeros(500000)
    print("arr:", arr[:10])
    recv_into(arr, c)
    print("arr:", arr[:10])


if __name__ == "__main__":
    main()

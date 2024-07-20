# my_package/b.py

from .a import A


class B(A):
    def bar():
        print("B.bar")

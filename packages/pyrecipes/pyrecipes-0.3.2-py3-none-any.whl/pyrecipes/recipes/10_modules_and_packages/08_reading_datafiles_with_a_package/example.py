"""
Your package includes a datafile that your code needs to read. You need to do this in
the most portable way possible.
"""

import sys
from pathlib import Path
from pyrecipes.utils.text import tree

example_dir = Path(__file__).parent / "src"
sys.path.append(str(example_dir))

import mypackage


def main():
    print("Suppose you have a package with files organized as follows:\n")
    for file in tree(example_dir):
        print(file)

    print(
        "Now suppose the file spam.py wants to read the contents of the file somedata.dat.\n"
        "To do that, use the following code:"
    )
    print(
        """
          # spam.py

          import pkgutil
          data = pkgutil.get_data(__package__, "somedata.dat")
          """
    )
    print(mypackage.spam.get_data())


if __name__ == "__main__":
    main()

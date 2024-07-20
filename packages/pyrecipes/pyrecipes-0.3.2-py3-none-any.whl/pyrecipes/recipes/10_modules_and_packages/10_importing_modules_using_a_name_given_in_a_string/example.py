"""
You have a name of a module that you would like to import, but it's being
held in a string. You would like to invoke the import command on the string.
"""

import importlib


def main():
    modules_to_import = ["itertools", "functools", "math"]
    for name in modules_to_import:
        print(f"Importing {name}")
        module = importlib.import_module(name)
        print(module, "\n")


if __name__ == "__main__":
    main()

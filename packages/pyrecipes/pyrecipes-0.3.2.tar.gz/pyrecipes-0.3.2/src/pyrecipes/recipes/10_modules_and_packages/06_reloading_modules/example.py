"""
You want to reload an already loaded module because you've made
changes to its source.
"""


def main():
    import pyrecipes
    import importlib

    print("Reloading pyrecipes...", end=" ")
    importlib.reload(pyrecipes)
    print("Done")


if __name__ == "__main__":
    main()

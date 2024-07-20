"""
You have a program that has grown beyond a simple script into an application
involving multiple files. You'd like to have some easy way for users to
run the program.
"""

from pathlib import Path
from pyrecipes.utils.text import tree


def main():
    example_path = Path(__file__).parent / "src"
    print(
        "If your application has grown into multiple files, you can put it into"
        "its own directory and add a __main__.py file. For example, you can create a directory like this:\n"
    )
    for file in tree(example_path):
        print(file)

    print(
        "\nIf __main__.py is present, you can simply run the Python interpreter on the top-level"
        "directory like this:\n\t> python myapplication"
    )


if __name__ == "__main__":
    main()

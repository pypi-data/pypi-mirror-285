"""
You have a module that you would like to split into multiple files. However,
you would like to do it without breaking existing code by keeping the
separate files unified as a single logical module.
"""

from pathlib import Path
from pyrecipes.utils.text import tree


def main():
    example_path = Path(__file__).parent / "src"
    print("Consider the following module, 'my_module.py':\n")
    print("-" * 25)
    print((Path(__file__).parent / "my_module.py").read_text())
    print("-" * 25)
    print(
        "\nThis can be split into a package with multiple modules like the following structure:\n"
    )
    for line in tree(example_path):
        print(line)

    print("\n\nThen each file would have the following code:\n")
    for file in sorted(example_path.glob("my_module/*.py")):
        print("-" * 25)
        print(file.read_text())
        print()


if __name__ == "__main__":
    main()

"""
You want to organise your code into a package consisting of a hierarchical
collection of modules.
"""

from pathlib import Path
import textwrap
from pyrecipes.utils.text import tree


def main():
    print(
        textwrap.dedent(
            """
            To define a python package, simply organise your code on your file system
            into a sensible directory/file structure and add an '__init__.py' file
            in every directory.

            For example, here would be a structure for a 'graphics' package,
            with subpackages 'primitive' with modules 'line', 'fill' & 'text'
            and subpackage 'formats' with modules 'png' & 'jpg':

            """
        )
    )

    for line in tree(Path(__file__).parent / "src"):
        print(line)
    print(
        textwrap.dedent(
            """

            With this done you should be able to perform various import statements
            such as the following:

            import graphics.primitive.line
            from graphics.primitive import line
            import graphics.formats.jpg as jpg
            """
        )
    )


if __name__ == "__main__":
    main()

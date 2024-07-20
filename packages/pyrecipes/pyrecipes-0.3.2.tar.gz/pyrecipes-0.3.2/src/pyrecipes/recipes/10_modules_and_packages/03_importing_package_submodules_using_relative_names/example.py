"""
You have code organised as a package and want to import a submodule
from one of the other package submodules without hardcoding the
package name into the import statement.
"""

import textwrap
from pathlib import Path
from pyrecipes.utils.text import tree


def main():
    print(
        textwrap.dedent(
            """
            Suppose you have a package with the following structure:

            """
        )
    )

    for line in tree(Path(__file__).parent / "src"):
        print(line)

    print(
        textwrap.dedent(
            """
            You can use relative import statements to control the imports between these modules.

            Suppose for example within the module 'my_package.A.spam' you need to import both
            'my_package.A.grok' and 'my_package.B.bar', you can use the following statements:

            # my_package/A/spam.py
            from . import grok
            from ..B import bar
            """
        )
    )


if __name__ == "__main__":
    main()

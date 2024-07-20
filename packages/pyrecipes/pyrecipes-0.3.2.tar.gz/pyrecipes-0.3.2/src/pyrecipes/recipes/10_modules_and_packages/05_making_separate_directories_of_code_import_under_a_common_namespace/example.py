"""
You have a large base of code with parts maintained and distributed
by different people. Each part is organised as a directory of files,
like a package. However, instead of having each part installed as a separate
named package, you would like all of the parts to join together under a common
package prefix.
"""

import sys
from pathlib import Path
from pyrecipes.utils.text import tree


def main():
    example_path = Path(__file__).parent / "src"
    print("Consider the following directories of Python packages: \n")
    print("-" * 25)

    for line in tree(example_path):
        print(line)

    print(
        "\n\nNotice that each of 'foo-package' and 'bar-package' have a common namespace 'spam'.\n"
        "Notice also that an '__init__.py' file is omitted from each of the 'spam' directories.\n"
        "This mechanism is known as a 'namespace' package. The following code should then work:\n"
    )
    print(
        """
    import sys
    sys.path.extend(["foo-package", "bar-package"])

    import spam.grok
    import spam.blah

    print(spam.grok.GROK)
    print(spam.blah.BLAH)
    """
    )

    sys.path.extend(
        [str(example_path / "foo-package"), str(example_path / "bar-package")]
    )

    import spam.grok
    import spam.blah

    print(spam.grok.GROK)
    print(spam.blah.BLAH)


if __name__ == "__main__":
    main()

"""
You want precise control over the symbols that are exported from a module
or package when a user uses the 'from module import *' statement.
"""

import textwrap


def main():
    print(
        textwrap.dedent(
            """
            Simply define a variable '__all__' in your module that explicly
            lists the exported names. For examples:

            # somemodule.py

            def spam():
                pass

            def grok():
                pass

            blah = 42

            # Only export 'spam' and 'grok'
            __all__ = ['spam', 'grok']"""
        )
    )


if __name__ == "__main__":
    main()

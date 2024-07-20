"""
You've written a useful library, and you want to be able to give it away to others.
"""


def main():
    print(
        """
Create a pyproject.toml file (https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

# pyproject.toml
[build-system]
requires = ["setuptools", "setuptools-scm"]
build-backend = "setuptools.build_meta"

[project]
name = "my_package"
authors = [
    {name = "Joe Bloggs", email = "joe.bloggs@example.com"},
]
description = "My package description"
readme = "README.md"
requires-python = ">=3.10"
keywords = ["one", "two"]
license = {text = "BSD-3-Clause"}
classifiers = [
    "Programming Language :: Python :: 3",
]
dependencies = [
    "requests",
    'importlib-metadata; python_version<"3.13"',
]
dynamic = ["version"]

[project.optional-dependencies]
pdf = ["ReportLab>=1.2", "RXP"]
rest = ["docutils>=0.3", "pack ==1.1, ==1.3"]

[project.scripts]
my-script = "my_package.module:function"

# ... other project metadata fields as listed in:
#     https://packaging.python.org/en/latest/guides/writing-pyproject-toml/


To build the package - from the package root directory - you can simply run:

    python -m build


To distribute to the test PyPi repository, you can use the following command:
    python -m twine upload --repository testpypi dist/*
    """
    )


if __name__ == "__main__":
    main()

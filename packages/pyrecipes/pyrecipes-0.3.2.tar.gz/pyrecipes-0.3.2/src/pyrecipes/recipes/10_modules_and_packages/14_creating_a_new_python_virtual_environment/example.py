"""
You want to create a new Python environment in which you can install modules
and packages. However, you want to do this without installing a new copy of
Python or making changes that might affect the system Python installation.
"""


def main():
    print(
        """
    The simplest solution is to use the built-in venv (https://docs.python.org/3/library/venv.html) module:

    # Create the environment
    python -m venv /path/to/environment

    # Activate the environment
    . /path/to/environment/activate


    Alternative third-party tools to consider could be:
      - virtualenv (https://virtualenv.pypa.io/en/latest/)
      - virtualenvwrapper (https://virtualenvwrapper.readthedocs.io/en/latest/)
    """
    )


if __name__ == "__main__":
    main()

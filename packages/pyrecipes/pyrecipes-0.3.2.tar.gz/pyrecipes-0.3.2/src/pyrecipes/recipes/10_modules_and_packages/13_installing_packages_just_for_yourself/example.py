"""
You want to install a third-party package, but you don't have permission
to install packages into the system Python. Alternatively, perhaps you
just want to install a package for your own use, not all users on the system.
"""


def main():
    print(
        """
    Simply use the pip command:
    pip install --user packagename
    """
    )


if __name__ == "__main__":
    main()

"""
You have Python code that can't be imported because it's not located
in a directory listed in sys.path. You would like to add new directories
to Python's path, but don't want to hardwire it into your code.
"""


def main():
    print(
        """
          There are two common ways to achieve this:

            1) Update the PYTHONPATH environment variable.
              e.g.
              Mac / linux:
                export PYTHONPATH="/some/dir:/some/other/dir:$PYTHONPATH"
              Windows Powershell:
                $env:PYTHONPATH="C:\\Users\\YourName\\some_dir;$PYTHONPATH"

            2) Create a '.pth' file that lists additional directories in the site-packages directory.
              e.g.
              Mac / Linux
              Typically site-packages is: /usr/local/lib/python3.x/site-packages

              # myapplication.pth
              /some/dir
              /some/other/dir

              Windows
              Typically site-packages is: %APPDATA%\\Python\\PythonXY\\site-packages

              # myapplication.pth
              C:\\Users\\YourName\\some_dir
          """
    )


if __name__ == "__main__":
    main()

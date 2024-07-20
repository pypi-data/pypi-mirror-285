import pkgutil


def get_data():
    return pkgutil.get_data(__package__, "somedata.dat")

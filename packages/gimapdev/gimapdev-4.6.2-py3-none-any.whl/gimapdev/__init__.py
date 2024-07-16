import os

from .__version__ import __version__


def get_file(file):
    folder = os.path.dirname(__file__)
    file = os.path.join(folder, file)
    return os.path.abspath(file).replace('\\', '/')

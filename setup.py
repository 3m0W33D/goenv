from setuptools import setup, find_packages
from goenv.__init__ import __version__
with open("requirements.txt") as fh:
    reqs = fh.read().split()
setup(
    name = "pygoenv",
    version = __version__,
    packages = find_packages(),

    install_requires = reqs,

    entry_points = {
        'console_scripts': [ 'goenv = goenv:main' ],
    },

    # metadata for upload to PyPI
    author = "Paul Woolcock",
    author_email = "paul@woolcock.us",
    description = "Simple environment manager for the Go programming language",
    license = "MIT",
    # keywords = "hello world example examples",
    url = "https://github.com/pwoolcoc/goenv",
)



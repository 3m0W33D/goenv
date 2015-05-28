from setuptools import setup, find_packages
import goenv
setup(
    name = "pygoenv",
    version = goenv.__version__,
    packages = find_packages(),

    install_requires = [
        'requests>=2.2.0',
        'docopt>=0.2.6',
    ],

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



from setuptools import setup, find_packages
setup(
    name = "pygoenv",
    version = "1.1",
    packages = find_packages(),

    install_requires = ['requests>=2.7.0'],

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



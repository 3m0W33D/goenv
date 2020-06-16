#!/usr/bin/env python
u"""
goenv

This is intended to be a cross-platform way to quickly set up
a go environment, including downloading and extracting the necessary
Golang distribution. Currently, the supported platforms are Linux,
Mac OSX, and FreeBSD

Usage:
  goenv <basedir> [-g <version> | --go-version=<version>] [--exclude=<path>]... [--install-only] [-q | --quiet]

Options:
  <basedir>                       the path to create your new goenv
  -g <version>, --go-version=<version>      specify a version of Go _other_ than the latest
  --exclude=<path>                          exclude a directory from the $GOPATH
  --install-only                            only download and install the specified version of Go, don't drop into a shell
  -q, --quiet                               only output messages that could be helpful in automated scripts
"""
from __future__ import print_function, absolute_import

__version__ = "2.0.0"

import os
import sys

from .constants import GOENV_CACHE_HOME, GOENV_CONFIG_HOME, GOLANG_DISTRIBUTIONS_DIR
from .platform_dependent import Linux, MacOSX, FreeBSD
from .utils import message, default_version, find_for_gopath, ensure_paths, \
                  substitute, ParseGoDL

def main():
    from docopt import docopt
    args = docopt(__doc__, version=__version__)

    args_exclude = args.get('--exclude')
    exclude = []
    if args_exclude:
        exclude = [os.path.realpath(e) for e in args_exclude]

    version = args.get('--go-version') if args.get('--go-version') is not None else default_version()

    #Accessing Globals
    global GOENV_CACHE_HOME
    global GOENV_CONFIG_HOME
    global GOLANG_DISTRIBUTIONS_DIR
    
    #Getting the new path
    newgoenv = substitute(args.get('<basedir>'))
    gopath = [newgoenv]

    GOENV_CONFIG_HOME = os.path.join(newgoenv,GOENV_CONFIG_HOME)
    GOENV_CACHE_HOME = os.path.join(GOENV_CONFIG_HOME,GOENV_CACHE_HOME)
    GOLANG_DISTRIBUTIONS_DIR = os.path.join(GOENV_CONFIG_HOME,GOLANG_DISTRIBUTIONS_DIR)
    quiet = args.get('--quiet')

    ensure_paths(GOENV_CONFIG_HOME,GOENV_CACHE_HOME, GOLANG_DISTRIBUTIONS_DIR, quiet=quiet)

    platforms = {
            "linux": Linux,
            "darwin": MacOSX,
            "freebsd": FreeBSD
    }

    for key in platforms:
        if sys.platform.startswith(key):
            impl = platforms.get(key)
            break
    else:
        message("Your platform '{}' is not supported, sorry!".format(sys.platform), sys.stderr, quiet)

    install_only = args.get('--install-only')
    impl(version, *gopath, install_only=install_only, quiet=quiet).go({
        "config":GOENV_CONFIG_HOME,
        "cache" :GOENV_CACHE_HOME,
        "distrib": GOLANG_DISTRIBUTIONS_DIR
    })


if __name__ == u'__main__':
    main()

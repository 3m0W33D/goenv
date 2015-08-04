#!/usr/bin/env python
u"""
goenv

This is intended to be a cross-platform way to quickly set up
a go environment, including downloading and extracting the necessary
Golang distribution. Currently, the supported platforms are Linux,
Mac OSX, and FreeBSD

Usage:
  goenv [--basedir=<basedir>] [-g <version> | --go-version=<version>] [--exclude=<path>]... [--install-only] [-q | --quiet]

Options:
  --basedir=<basedir>                       the directory to start looking for locations to add to the GOPATH [default: .]
  -g <version>, --go-version=<version>      specify a version of Go _other_ than the latest
  --exclude=<path>                          exclude a directory from the $GOPATH
  --install-only                            only download and install the specified version of Go, don't drop into a shell
  -q, --quiet                               only output messages that could be helpful in automated scripts
"""
from __future__ import print_function

__version__ = "1.4.1"

import os
import sys

from constants import XDG_CACHE_HOME, XDG_CONFIG_HOME, \
                      GOENV_CACHE_HOME, GOENV_CONFIG_HOME, \
                      GOLANG_DISTRIBUTIONS_DIR
from platform import Linux, MacOSX, FreeBSD
from utils import message, default_version, find_for_gopath, ensure_paths, \
                  substitute, ParseGoDL

def main():
    from docopt import docopt
    args = docopt(__doc__, version=__version__)

    args_exclude = args.get('--exclude')
    exclude = []
    if args_exclude:
        exclude = [os.path.realpath(e) for e in args_exclude]

    version = args.get('--go-version') if args.get('--go-version') is not None else default_version()

    gopath = find_for_gopath(substitute(args.get('--basedir')), exclude)

    # we should have _something_ in the GOPATH...
    if not gopath:
        gopath = [ os.getcwd() ]

    quiet = args.get('--quiet')
    ensure_paths(GOENV_CACHE_HOME, GOENV_CONFIG_HOME, GOLANG_DISTRIBUTIONS_DIR, quiet=quiet)

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
    impl(version, *gopath, install_only=install_only, quiet=quiet).go()


if __name__ == u'__main__':
    main()

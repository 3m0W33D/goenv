#!/usr/bin/env python
from __future__ import print_function

USAGE = u"""
This is intended to be a cross-platform way to quickly set up
a go environment, including downloading and extracting the necessary
Golang distribution. Currently, the supported platforms are Linux
and Mac OSX
"""

import argparse
import os
import sys

from constants import XDG_CACHE_HOME, XDG_CONFIG_HOME, \
                      GOENV_CACHE_HOME, GOENV_CONFIG_HOME, \
                      GOLANG_DISTRIBUTIONS_DIR
from platform import Linux, MacOSX, FreeBSD
from utils import default_version, find_for_gopath, ensure_paths, \
                  substitute, ParseGoDL

def main():
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument("--basedir", default='.', help="the directory to start looking for locations to add to the GOPATH")
    parser.add_argument("--go-version", dest='version', action='store',
            default=None, help="specify a version of Go _other_ than the latest")
    parser.add_argument("--exclude", default=tuple(), dest='exclude',
            action='store', nargs='*', help="exclude a directory from the $GOPATH")
    parser.add_argument("--install-only", default=False, dest="install_only", action='store_true',
            help="only download and install the specified version of Go, don't drop into a shell")
    parser.add_argument("-q", "--quiet", default=False, dest="quiet", action="store_true",
                        help="only output messages that could be helpful in automated scripts")
    parser.add_argument("-x", "--no-vendor", default=False, dest="no_vendor",
            action="store_true", help="Don't create a `vendor` directory at the top level of the project")

    args = parser.parse_args()

    if args.exclude is not None:
        exclude = [os.path.realpath(e) for e in args.exclude]

    if args.version is None:
        args.version = default_version()

    gopath = find_for_gopath(substitute(args.basedir), exclude)

    # we should have _something_ in the GOPATH...
    if not gopath:
        gopath = [ os.getcwd() ]

    if not args.no_vendor:
        vendor_path = substitute("vendor")
        ensure_paths(vendor_path)
        gopath.insert(0, vendor_path)

    ensure_paths(GOENV_CACHE_HOME, GOENV_CONFIG_HOME, GOLANG_DISTRIBUTIONS_DIR, quiet=args.quiet)

    if sys.platform.startswith("linux"):
        impl = Linux
    elif sys.platform.startswith("darwin"):
        impl = MacOSX
    elif sys.platform.startswith("freebsd"):
        impl = FreeBSD

    impl(args.version, *gopath, install_only=args.install_only, quiet=args.quiet).go()


if __name__ == u'__main__':
    main()

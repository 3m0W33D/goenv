#!/usr/bin/env python
from __future__ import print_function

USAGE = u"""
This is intended to be a cross-platform way to quickly set up
a go environment, including downloading and extracting the necessary
Golang distribution. Currently, the supported platforms are Linux
and Mac OSX
"""


import argparse
import httplib
import math
import os
import platform
import sys
import tarfile

from HTMLParser import HTMLParser

DOWNLOAD_HOSTNAME = "storage.googleapis.com"
DOWNLOAD_PATH = "/golang/{filename}"
DOWNLOAD_FILENAME = "go{version}.{platform}-{architecture}.{extension}"


XDG_CACHE_HOME = os.environ.get('XDG_CACHE_HOME', False) or \
                 os.path.join(os.environ['HOME'], ".cache")
XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME') or \
                  os.path.join(os.environ['HOME'], ".config")
GOENV_CACHE_HOME = os.path.join(XDG_CACHE_HOME, "goenv")
GOENV_CONFIG_HOME = os.path.join(XDG_CONFIG_HOME, "goenv",)
GOLANG_DISTRIBUTIONS_DIR = os.path.join(GOENV_CONFIG_HOME, "dists")


class Plat(object):
    def __init__(self, version=None, *gopath, **opts):
        if version is None:
            version = self.latest_version()
        self.version = version
        self.gopath = gopath
        self.opts = opts

    def quiet(self):
        return self.opts.get("quiet", False)

    def message(self, msg, file=sys.stdout, override=False):
        return message(msg, file, self.quiet(), override)

    def print_progress(self, total_read, buf_size, total_size):
        fraction = float(total_read) / total_size
        pct = round(fraction * 100, 2)
        read_kb = int(total_read) / 1024
        total_kb = int(total_size) / 1024
        num_blocks = int(math.floor(pct)) / 2
        bar = (("=" * (num_blocks - 1)) + ">")
        sys.stdout.write("\r[{3:<50}] {0:>6}% ({1} / {2} kb)".format(
                                pct, 
                                int(read_kb), 
                                int(total_kb),
                                bar))
        if total_read >= total_size:
            print("\n")

    def do_download(self, resp, report_hook=None, bufsize=8192):
        if report_hook is None:
            report_hook = self.print_progress
        total_size = int(resp.getheader("Content-Length").strip())
        total_read = 0
        whole = []

        while True:
            part = resp.read(bufsize)
            total_read = total_read + len(part)

            if not part:
                break

            whole.append(part)
            report_hook(total_read, bufsize, total_size)
        return "".join(whole)

    def download(self):
        version = self.version
        architecture = self.architecture
        extension = self.extension
        platform = self.platform

        filename = DOWNLOAD_FILENAME.format(version=version,
                                            platform=platform,
                                            architecture=architecture,
                                            extension=extension)
        path = DOWNLOAD_PATH.format(filename=filename)
        fullpath = os.path.join(GOENV_CACHE_HOME, filename)
        if not os.path.exists(fullpath):
            self.message("Downloading http://{0}{1}".format(DOWNLOAD_HOSTNAME, path), file=sys.stderr)
            try:
                connection = httplib.HTTPConnection(DOWNLOAD_HOSTNAME)
                connection.request("GET", path)
                response = self.do_download(connection.getresponse(buffering=True))
            except httplib.HTTPException as ex:
                self.message(ex.message, file=sys.stderr)
                sys.exit(1)

            with open(fullpath, 'wb+') as f:
                f.write(response)
        else:
            self.message("Using existing tarball", file=sys.stderr)
        return fullpath


class Unix(Plat):
    def _is_64bit(self):
        return sys.maxsize > 2**32

    def do_subshell(self):
        return u"install_only" not in self.opts or \
                not self.opts.get(u"install_only")

    def go(self):
        godir = self.extract(self.download())
        if self.do_subshell():
            self.subshell(godir, *self.gopath)
        else:
            goroot = self.goroot(godir)
            if not self.quiet():
                message = """Go installed, run the following commands (for your shell) to start using Go.

bash/zsh:

    export GOROOT={0}
    export PATH="{0}/bin:${{PATH}}"

csh/tcsh:

    setenv GOROOT {0}
    setenv PATH {0}/bin:$PATH

fish:

    set -xg GOROOT {0}
    set -xg PATH {0}/bin $PATH

"""
                override = False
            else:
                message = "{0}"
                override = True

            self.message(message.format(goroot), override=override)

    def goroot(self, godir):
        return os.path.join(godir, "go")

    def subshell(self, godir, *gopath):
        version = self.version
        if gopath:
            gopath = ":".join(gopath)

        goroot = os.path.join(godir, "go")
        gobin = os.path.join(goroot, "bin")
        newpath = ":".join([gobin, os.environ.get("PATH", "")])

        additionalenv = {
                "PATH": newpath,
                "GOROOT": goroot,
                "GOPATH": gopath,
                "GOENV": version,
        }
        newenv = os.environ.copy()
        newenv.update(**additionalenv)
        os.execlpe(os.environ.get("SHELL", '/bin/bash'), "", newenv)

    def extract(self, filename):
        version = self.version
        godir = os.path.join(GOLANG_DISTRIBUTIONS_DIR, version)
        if not os.path.exists(godir):
            self.message("Extracting {0} to {1}".format(filename, godir), file=sys.stderr)
            with tarfile.open(filename) as tarball:
                tarball.extractall(godir)
        else:
            self.message("Go version {0} already exists, skipping extract".format(version), file=sys.stderr)
        return godir

    def download(self):
        return super(Unix, self).download()


class FreeBSD(Unix):
    def __init__(self, *args, **kwargs):
        self.platform = "freebsd"
        self.architecture = "amd64" if self._is_64bit() else "386"
        self.extension = "tar.gz"
        super(FreeBSD, self).__init__(*args, **kwargs)

class Linux(Unix):
    def __init__(self, *args, **kwargs):
        self.platform = "linux"
        self.architecture = "amd64" if self._is_64bit() else "386"
        self.extension = "tar.gz"

        super(Linux, self).__init__(*args, **kwargs)


class MacOSX(Unix):
    def __init__(self, *args, **kwargs):
        self.platform = "darwin"
        arch = "amd64" if self._is_64bit() else "386"
        v, _, _ = platform.mac_ver()
        _, minor, _ = v.split('.')

        if minor < 8:
            osx_version = "10.6"
        elif minor >= 8:
            osx_version = "10.8"

        self.architecture = "{0}-osx{1}".format(arch, osx_version)
        self.extension = "tar.gz"

        super(MacOSX, self).__init__(*args)

class ParseGoDL(HTMLParser):
    """
    Kinda janky, but I like it better than running a regex over the html
    """
    in_page, in_container, latest = (False,) * 3
    def handle_starttag(self, data, attrs_l):
        if self.latest:
            return
        attrs = dict(attrs_l)
        id = attrs.get("id", "")
        cls = attrs.get("class", "")
        if id == "page":
            self.in_page = True
            return
        if self.in_page and cls == "container":
            self.in_container = True
            return
        if not (self.in_page and self.in_container):
            return
        if not id.startswith("go"):
            return
        self.latest = id[2:]

# Helper functions
def message(message, file, quiet=False, override=False):
    if not quiet or (quiet and override):
        print(message, file=file)

def default_version():
    conn = httplib.HTTPConnection("golang.org"); conn.connect()
    conn.request("GET", "/dl/")
    resp = conn.getresponse()
    if resp.status // 100 != 2:
        return raw_input("Error detecting the default Go version.\nPlease enter the version you wish to install (i.e., 1.3): ")
    body = resp.read()
    parser = ParseGoDL()
    parser.feed(body)
    return parser.latest

def all_for_gopath(base):
    return [substitute(loc) for (loc, dirs, files) in os.walk(base) if 'src' in dirs]


def find_for_gopath(base, exclude=None):
    if exclude is None:
        exclude = []
    alldirs = all_for_gopath(base)
    return [ d for d in alldirs if d not in exclude]


def ensure_paths(*paths, **kwds):
    quiet = kwds.pop("quiet", False)
    for path in paths:
        if not os.path.exists(path):
            message("creating {0}".format(path), file=sys.stderr, quiet=quiet)
            os.makedirs(path)


def substitute(path):
    if path == '.':
        return os.environ['PWD']
    elif path == '..':
        return os.path.dirname(os.environ['PWD'])
    return os.path.realpath(path)


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

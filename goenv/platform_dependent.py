#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import math
import os
import sys
import tarfile
import platform
from clint.textui import progress

from constants import XDG_CACHE_HOME, XDG_CONFIG_HOME, \
                      GOENV_CACHE_HOME, GOENV_CONFIG_HOME, \
                      GOLANG_DISTRIBUTIONS_DIR, DOWNLOAD_HOSTNAME, \
                      DOWNLOAD_PATH, DOWNLOAD_FILENAME

from utils import message

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

    def do_download(self, resp, report_hook=None, bufsize=1024):
        total_size = int(resp.headers.get("Content-Length").strip())
        total_read = 0
        whole = []

        for part in progress.bar(resp.iter_content(bufsize), expected_size=(total_size / bufsize) + 1, label='KB '):
            total_read = total_read + len(part)

            if not part:
                break

            whole.append(part)

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
            url = "http://{0}{1}".format(DOWNLOAD_HOSTNAME, path)
            self.message("Downloading {0}".format(url), file=sys.stderr)
            try:
                response = self.do_download(requests.get(url, stream=True))
            except requests.exceptions.RequestException as ex:
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



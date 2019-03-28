#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import math
import os
import sys
import tarfile
import platform
from clint.textui import progress

from .constants import XDG_CACHE_HOME, XDG_CONFIG_HOME, \
                      GOENV_CACHE_HOME, GOENV_CONFIG_HOME, \
                      GOLANG_DISTRIBUTIONS_DIR, DOWNLOAD_HOSTNAME, \
                      DOWNLOAD_PATH, DOWNLOAD_FILENAME

from .utils import message

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

        return b"".join(whole)

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
        return "install_only" not in self.opts or \
                not self.opts.get("install_only")

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

        # additionalenv = {
        #         "PATH": newpath,
        #         "GOROOT": goroot,
        #         "GOPATH": gopath,
        #         "GOENV": version,
        # }
        # newenv = os.environ.copy()
        # newenv.update(**additionalenv)
        # os.execlpe(os.environ.get("SHELL", '/bin/bash'),"bash", newenv)
        activate_sh="""
        

# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

deactivate_go () {
    # reset old environment variables
    if [ -n "$_OLD_GO_PATH" ] ; then
        export PATH="$_OLD_GO_PATH"
        unset _OLD_GO_PATH
        unset GOENV
        unset GOROOT
        unset GOCACHE
        unset GOPATH
    fi
    #Checking if gopath is valid previously
    if [ -n "$_OLD_GOPATH" ]; then
        export GOPATH="$_OLD_GOPATH"
        unset _OLD_GOPATH
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
        hash -r
    fi

    if [ -n "$_OLD_GO_VIRTUAL_PS1" ] ; then
        PS1="$_OLD_GO_VIRTUAL_PS1"
        export PS1
        unset _OLD_GO_VIRTUAL_PS1
    fi

    if [ ! "$1" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate_go
    fi
}

# unset irrelevant variables
deactivate_go nondestructive

# find the directory of this script
# http://stackoverflow.com/a/246128
if [ -n "$GOPATH" ] ; then
    _OLD_GOPATH="$GOPATH"
fi

if [ "${BASH_SOURCE}" ] ; then
    SOURCE="${BASH_SOURCE[0]}"

    while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
    DIR="$( command cd -P "$( dirname "$SOURCE" )" > /dev/null && pwd )"

    GOPATH="$(dirname "$DIR")"
else
    # dash not movable. fix use case:
    #   dash -c " . node-env/bin/activate && node -v"
    GOPATH="__GOPATH__"
fi

# GOPATH is the parent of the directory where this script is
export GOPATH

#Adding GOROOT to executables
export GOROOT="__GOROOT__"

#Setting new path 
_OLD_GO_PATH="$PATH"
export PATH="$GOPATH/bin:$GOROOT/bin:$PATH"

# Adding local caching
export GOCACHE="$GOPATH/.cache"

#In case of virtualgo is being used
export VIRTUALGO_ROOT="$GOPATH/.virtualgo"

#Adding GOENV
export GOENV="__VER__"


if [ -z "$GO_VIRTUAL_ENV_DISABLE_PROMPT" ] ; then
    _OLD_GO_VIRTUAL_PS1="$PS1"
    if [ "x(testgo)" != x ] ; then
        PS1="(testgo) $PS1"
    else
    if [ "`basename "$GOPATH"`" = "___" ] ; then
        # special case for Aspen magic directories
        # see http://www.zetadev.com/software/aspen/
        PS1="[`basename \`dirname "$GOPATH"\``] $PS1"
    else
        PS1="(`basename "$GOPATH"`) $PS1"
    fi
    fi
    export PS1
fi

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
    hash -r
fi

#Install virtualgo command into the activate script instead of the bashrc
""".replace("__GOPATH__",gopath).replace("__GOROOT__",goroot).replace("__VER__",version)
        os.makedirs(gopath+"/bin/",exist_ok=True)
        with open(gopath+"/bin/activate","w+") as f:
            f.write(activate_sh)
        self.message("Please use source bin/activate")

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
        self.architecture = "amd64" if self._is_64bit() else "386"
        self.extension = "tar.gz"

        super(MacOSX, self).__init__(*args)


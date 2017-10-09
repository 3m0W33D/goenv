#!/usr/bin/env python
from __future__ import print_function

import requests
import re
import os
import sys

from .compat import HTMLParser

def message(message, file, quiet=False, override=False):
    if not quiet or (quiet and override):
        print(message, file=file)

def default_version():
    r = requests.get("https://golang.org/")
    if r.status_code // 100 != 2:
        return raw_input("Error detecting the default Go version.\nPlease enter the version you wish to install (i.e., 1.3): ")
    body = r.content.decode("utf-8")

    reg = re.compile("Build version go(.+)\.<br>")
    m = re.search(reg, body)
    return m.group(1)

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



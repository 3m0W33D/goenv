#!/usr/bin/env python

import os

XDG_CACHE_HOME = os.environ.get('PWD', False) or \
                 os.path.join(os.environ['HOME'], ".cache")
XDG_CONFIG_HOME = os.environ.get('PWD') or \
                  os.path.join(os.environ['HOME'], ".config")
GOENV_CACHE_HOME = os.path.join(XDG_CACHE_HOME, ".goenv")
GOENV_CONFIG_HOME = os.path.join(XDG_CONFIG_HOME, ".goenv",)
GOLANG_DISTRIBUTIONS_DIR = os.path.join(GOENV_CONFIG_HOME, "dists")

DOWNLOAD_HOSTNAME = "storage.googleapis.com"
DOWNLOAD_PATH = "/golang/{filename}"
DOWNLOAD_FILENAME = "go{version}.{platform}-{architecture}.{extension}"


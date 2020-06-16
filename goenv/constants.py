#!/usr/bin/env python

import os

XDG_CACHE_HOME = os.environ.get('PWD', False) or \
                 os.path.join(os.environ['HOME'], ".cache")
XDG_CONFIG_HOME = os.environ.get('PWD') or \
                  os.path.join(os.environ['HOME'], ".config")
GOENV_CACHE_HOME = "downloads"
GOENV_CONFIG_HOME = ".goenv"
GOLANG_DISTRIBUTIONS_DIR = "dists"

DOWNLOAD_HOSTNAME = "storage.googleapis.com"
DOWNLOAD_PATH = "/golang/{filename}"
DOWNLOAD_FILENAME = "go{version}.{platform}-{architecture}.{extension}"


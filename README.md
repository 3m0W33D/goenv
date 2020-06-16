# goenv - Set up a Golang environment

Fork of the original goenv. Fixed for python3 and added activate scripted based on virtualenv from python
<!-- I got tired of manually setting my GOPATH when I went from one project to another,
so I wrote a small utility to set up my environment for me. It is similar in spirit to Python's
`virtualenv`, though it does less, and does it a little differently.

The main difference is that instead of an 'activate' script that sets up your environment,
this opens up a new subshell for you to work in. It will also download
and install the version of Go that you want it to. -->

## Installation

Currently goenv is written in python, so installation is not a simple `pip
install` away:

    $ sudo pip install git+https://github.com/3m0W33D/goenv.git

## Usage

    $ cd /path/to
    $ goenv project
    $ source project/bin/activate

    # specify Golang version
    $ goenv project --go-version 1.1
    Downloading http://go.googlecode.com/files/go1.1.linux-amd64.tar.gz

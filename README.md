# goenv - Set up a Golang environment

I got tired of manually setting my GOPATH when I went from one project to another,
so I wrote a small utility to set up my environment for me. It is similar in spirit to Python's
`virtualenv`, though it does less, and does it a little differently.

The main difference is that instead of an 'activate' script that sets up your environment,
this opens up a new subshell for you to work in. It will also download
and install the version of Go that you want it to.

It also supports vendoring dependencies by added a top-level `vendor`
directory to a project, and placing that directory first in the
`$GOPATH` so that dependencies fetched with `go get` will be placed
there.

## Installation

It is a single Python script, so you can just make it executable and put
it somewhere in your path.

    # you might need to add --no-check-certificate to the wget command...
    $ wget -O ~/bin/goenv https://raw.github.com/pwoolcoc/goenv/master/goenv
    # for the love of pete, don't just run scripts you get from the internet, check them first!
    $ $EDITOR ~/bin/goenv
    $ chmod +x ~/bin/goenv

## Usage

    $ cd /path/to/project
    $ echo $GOPATH

    # simplest usage
    $ goenv
    Downloading http://go.googlecode.com/files/go1.2.linux-amd64.tar.gz
    Extracting /home/user/.cache/goenv/go1.2.linux-amd64.tar.gz to /home/user/.config/goenv/dists/1.2
    (golang-1.2) $ echo $GOPATH
    /path/to/project:/path/to/project/pkg/somepkg
    ^D
    $
    
    # You don't have to download a new go tarball every time...
    $ goenv
    Using existing tarball
    Go version 1.2 already exists, skipping extract
    (golang-1.2) $
    ^D
    $

    # specify Golang version
    $ goenv --go-version 1.1
    Downloading http://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
    Extracting /home/user/.cache/goenv/go1.1.linux-amd64.tar.gz to /home/user/.config/goenv/dists/1.1
    (golang-1.1) $

## Contact

email: pwoolcoc@gmail.com

twitter: @pauldwoolcock

jabber: pauldwoolcock@dukgo.com

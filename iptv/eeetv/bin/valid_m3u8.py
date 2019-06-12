#!/usr/bin/python
# -*- coding: utf-8 -*-

# validate m3u8 format to identify broken playlist
#

import sys, os

__VERSION__ = "2019.06.12"

__ABOUT__  = "= m3u8 format validator = version %s =" % (__VERSION__)

__USAGE__  = """
%(about)s

usage: %(exe)s [-v[v]] filename.m3u8

to validate format of m3u8 file 'filename.m3u8' for batch processing

-v  ... verbose mode
-vv ... more verbose mode

exit codes:
    -1 ... missing parameter, usage help shown
     0 ... valid m3u8 file
     1 ... not valid m3u8 file
""" % { 'about': __ABOUT__, 'exe': sys.argv[0] }

VERBOSE = 0

# strings to expect on beginning of the line
#               0           1        2
EXPECT = [ '#EXTM3U', '#EXTINF:', '*' ]


def msg(level, txt):
    """ verbose output """
    if level > VERBOSE: return
    print txt

def expect_starts_with():
    """ return string to be expected the line starts with """
    i = 0
    while True:
        yield EXPECT[i]
        i = (i+1) if i<2 else 1

def line_stats_with(line, starts):
    """ startswith expanded with * to match anything """
    return True if starts == '*' else line.startswith(starts)

def m3u8_file(fname):
    """  validate fname for m3u8 format """
    msg(2, 'checking filename(%s) ...' % (fname))
    with open(fname) as f:
        expect_gen = expect_starts_with()
        for line in f:
            starts = expect_gen.next()
            if not line_stats_with(line, starts):
                msg(1, '"%s" does not start with "%s"' % (line.strip(), starts))
                return False
            msg(2, '"%s" starts with "%s"' % (line.strip(), starts))
    return True

def usage(n=1):
    """" """
    if len(sys.argv) > n: return
    print __USAGE__
    sys.exit(-1)


if __name__ == '__main__':

    usage()

    # the first par
    par = sys.argv[1]

    if par.startswith('-v'):
        VERBOSE = par.count('v')
        fname = sys.argv[2]
    else:
        fname = par
    #
    valid = m3u8_file(fname)

    sys.exit(0 if valid else 1)

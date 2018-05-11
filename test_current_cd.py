#!/usr/bin/env python3

import sys

try:
    import discid
except ImportError:
    print("You have to install discid")
    print("Maybe run 'pip install discid'?")
    sys.exit(1)

import cddb

if __name__ == "__main__":
    c = cddb.CDDBClient(discid.read())
    c.query()

#!/usr/bin/env python3

import sys

def err(msg, status=1):
    print(msg, file=sys.stderr)
    sys.exit(status)


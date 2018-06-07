#!/usr/bin/env python3

try:
    import simplejson as json
except ImportError:
    import json

import os
from mimetypes import guess_extension as guessExtension

from magic import Magic

mimeMagic = Magic(mime=True)

def guessMime(path):
    if os.path.isdir(path):
        return 'inode/directory'
    return mimeMagic.from_file(path)

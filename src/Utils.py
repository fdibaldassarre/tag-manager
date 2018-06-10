#!/usr/bin/env python3

try:
    import simplejson as json
except ImportError:
    import json

import os
import importlib.util
from mimetypes import guess_extension as guessExtension

from magic import Magic

mimeMagic = Magic(mime=True)

def guessMime(path):
    if os.path.isdir(path):
        return 'inode/directory'
    return mimeMagic.from_file(path)

def loadModuleFromPath(name, module_path):
    if not os.path.exists(module_path):
        return None
    spec = importlib.util.spec_from_file_location(name, module_path)
    custom = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custom)
    return custom

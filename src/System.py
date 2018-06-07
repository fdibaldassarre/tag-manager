#!/usr/bin/env python3

import os
from subprocess import Popen

from .Config import ConfigManager

def openFile(relpath):
    '''
        Try to open a file.

        :param str relpath: Path of the file relative to the configired root
        :return: False if the file was not found, True otherwise
        :rtype: bool
    '''
    fullpath = os.path.join(ConfigManager.getRoot(), relpath)
    fullpath = os.path.abspath(fullpath)
    if not os.path.exists(fullpath):
        return False
    Popen(['xdg-open', fullpath])
    return True

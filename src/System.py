#!/usr/bin/env python3

import os
from subprocess import Popen

from .dao import filesDao
from .Config import ConfigManager
from .Thumbnailer import Thumbnailer
from src.Utils import guessMime

thumbnailer = Thumbnailer(256)

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

def getRootRelativePath(path):
    '''
        Get the path relative to the profile root.

        :param str path: path
        :return: path relative to the root
        :rtype: str
    '''
    abspath = os.path.abspath(path)
    return os.path.relpath(abspath, ConfigManager.getRoot())

def addFile(path):
    '''
        Add a file to the database.

        :param str path: Path of the file to add
    '''
    name = os.path.relpath(path, ConfigManager.getRoot())
    # Get mime
    mime = guessMime(path)
    # Add to db
    file = filesDao.insert(name=name, mime=mime)
    # Create thumbnail
    thumbnailer.getThumbnail(file)
    return file

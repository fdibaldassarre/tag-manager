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

        :param str relpath: Path of the file relative to the configured root
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
        :return: path relative to the root and file name
        :rtype: str, str
    '''
    abspath = os.path.abspath(path)
    name = os.path.basename(abspath)
    folder = os.path.dirname(abspath)
    relpath = os.path.relpath(folder, ConfigManager.getRoot())
    return relpath, name

def addFile(path):
    '''
        Add a file to the database.

        :param str path: Path of the file to add
    '''
    relpath, name = getRootRelativePath(path)
    # Get mime
    mime = guessMime(path)
    # Add to db
    file = filesDao.insert(name=name, relpath=relpath, mime=mime)
    # Create thumbnail
    thumbnailer.getThumbnail(file)
    return file

def removeFile(file):
    '''
        Remove a file from database and open base folder
        to allow manual cleanup.

        :param dao.entities.IFileLazy: file
    '''
    filesDao.delete(file)
    thumbnailer.removeThumbnail(file)
    path = os.path.join(ConfigManager.getRoot(), file.name)
    if os.path.exists(path):
        if os.path.isdir(path):
            folder_to_open = path
        else:
            folder_to_open = os.path.dirname(path)
        # Open folder to delete manually
        openFile(folder_to_open)

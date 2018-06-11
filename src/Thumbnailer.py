#!/usr/bin/env python3

import os
from subprocess import Popen

try:
  from natsort import natsorted
except ImportError:
  def natsorted(data, f):
    it = list(data)
    it.sort()
    return it

from src.Config import ConfigManager
from src.Utils import guessMime

# Create/view file preview

VIDEO_MIMES = ["video/x-msvideo", "video/x-matroska", "video/mp4", "video/x-ogm+ogg", "video/x-ms-wmv"]
IMAGE_MIMES = ["image/gif", "image/png", "image/jpeg", "application/pdf", "image/vnd.djvu"]

THUMB_VIDEO = 0
THUMB_IMAGE = 1
THUMB_FOLDER = 2

THUMB_EXTENSION = '.png'

class Thumbnailer():

    def __init__(self, icon_size):
        self.thumbnails_folder = os.path.join(ConfigManager.profile_folder, "thumbnails/")
        self.thumbnails_fail_folder = os.path.join(ConfigManager.profile_folder, "thumbnails_fail/")
        self.icon_size = icon_size

    def getThumbnail(self, tfile):
        '''
            Return a thumbnail for the given file.

            :param IFile tfile: File
            :return: path of the thumbnail
            :rtype: str
        '''
        path = os.path.join(ConfigManager.getRoot(), tfile.name)
        if not os.path.exists(path):
            return None
        thumb_path = self._getThumbnailPath(tfile)
        if os.path.exists(thumb_path):
            return thumb_path
        fail_path = self._getThumbnailFailPath(tfile)
        thumb_type = self.getThumbnailType(path)
        if thumb_type is None:
            return None
        elif not os.path.exists(fail_path):
            self.createThumbnail(path, thumb_path, thumb_type)
            return path
        else:
            return None

    def _getThumbnailPath(self, tfile):
        '''
            Get the thumbail path for the given file.

            :param dao.entities.IFileLazy file: File
            :return: The path of the thumbnail (may not exist on filesystem)
            :rtype: str
        '''
        icon_folder = os.path.join(self.thumbnails_folder, str(self.icon_size))
        return os.path.join(icon_folder, str(tfile.id) + THUMB_EXTENSION)

    def _getThumbnailFailPath(self, tfile):
        icon_folder = os.path.join(self.thumbnails_fail_folder, str(self.icon_size))
        return os.path.join(icon_folder, str(tfile.id) + THUMB_EXTENSION)

    def removeThumbnail(self, tfile):
        '''
            Remove the thumbnails associated with the given file.

            :param dao.entities.IFileLazy tfile: File
        '''
        thumb_file = self._getThumbnailPath(tfile)
        thumb_fail_file = self._getThumbnailFailPath(tfile)
        if os.path.exists(thumb_file):
            os.remove(thumb_file)
        if os.path.exists(thumb_fail_file):
            os.remove(thumb_fail_file)

    def getThumbnailType(self, path):
        mime = guessMime(path)
        if mime == 'inode/directory':
            return THUMB_FOLDER
        elif mime in VIDEO_MIMES:
            return THUMB_VIDEO
        elif mime in IMAGE_MIMES:
            return THUMB_IMAGE
        return None

    def createThumbnail(self, path, thumb_file, thumb_type):
        print(path)
        thumb_folder = os.path.dirname(thumb_file)
        if not os.path.isdir(thumb_folder):
            os.makedirs(thumb_folder)
        if thumb_type == THUMB_VIDEO:
            self.createVideoThumbnail(path, thumb_file)
        elif thumb_type == THUMB_IMAGE:
            self.createImageThumbnail(path, thumb_file)
        elif thumb_type == THUMB_FOLDER:
            self.createFolderThumbnail(path, thumb_file)
        else:
            return False

    def createVideoThumbnail(self, path, thumb_file):
        args = ["ffmpegthumbnailer", "-i", path, "-o", thumb_file, "-s", str(self.icon_size) ]
        process = Popen(args)

    def createImageThumbnail(self, path, thumb_file):
        icon_format = str(self.icon_size) + "x" + str(self.icon_size)
        args = ["convert", path, "-thumbnail", icon_format, thumb_file]
        process = Popen(args)

    def createFolderThumbnail(self, path, thumb_file):
        fnames = self._getFilesInFolder(path)
        for fname in fnames:
            fpath = os.path.join(path, fname)
            if not os.path.isdir(fpath):
                mime = guessMime(fpath)
                if mime in VIDEO_MIMES:
                    self.createVideoThumbnail(fpath, thumb_file)
                    break
                elif mime in IMAGE_MIMES:
                    self.createImageThumbnail(fpath, thumb_file)
                    break

    def _getFilesInFolder(self, location):
        result = []
        for root, _, files in os.walk(location):
            for fname in files:
                result.append(os.path.join(root, fname))
        sr = natsorted(result, lambda x : x.lower())
        return sr

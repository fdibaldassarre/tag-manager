#!/usr/bin/env python3

import argparse
import os
import sys

from src.Config import ConfigManager

# Parse the command line argument
parser = argparse.ArgumentParser(description="Create thumbs")
parser.add_argument('filename', help='file name')
parser.add_argument('--profile', help='profile name', default='default')
parser.add_argument('--path', help='file to use for the thumbnail', default=None)

args = parser.parse_args()

# Configure the application
profile_folder = os.path.join(os.environ['HOME'], ".config/tag-manager/" + args.profile)
file_name = args.filename
path = args.path

if path is not None and not os.path.isfile(path):
    # Validate path
    print("Invalid path, must be a file")
    sys.exit(2)

ConfigManager.setup(profile_folder)

# Load the thumbnailer
from src.Thumbnailer import Thumbnailer
from src.dao import filesDao

thumbnailer = Thumbnailer(256)

files = filesDao.getByName(file_name)
print("Got %d files" % len(files))
if len(files) == 0:
    sys.exit(1)
tfile = files[0]
print("Creating thumbnail for %s" % tfile.name)
if path is not None:
    thumb = thumbnailer.createThumbnailFrom(tfile, path)
else:
    thumb = thumbnailer.recreateThumbnail(tfile)
print(thumb)

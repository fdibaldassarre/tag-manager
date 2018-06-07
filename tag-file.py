#!/usr/bin/env python3

import os
import argparse

parser = argparse.ArgumentParser(description="Tagger")
parser.add_argument('file', help='file to tag')
parser.add_argument('--profile', default='default', help='profile name, default: default')
parser.add_argument('--debug', action='store_true', help='debug')

args = parser.parse_args()

# Configure the application
from src.Config import ConfigManager

profile_folder = os.path.join(os.environ['HOME'], ".config/tag-manager/" + args.profile)
ConfigManager.setup(profile_folder)
ConfigManager.debug = args.debug

# Get the file
from src.Utils import guessMime
from src.Thumbnailer import Thumbnailer
from src.dao import filesDao

filepath = args.file
name = os.path.relpath(filepath, ConfigManager.getRoot())

file = filesDao.getByName(name)
if file is None:
    # Get mime
    mime = guessMime(filepath)
    # Add to db
    file = filesDao.insert(name=name, mime=mime)
    # Create thumbnail
    thumbnailer = Thumbnailer(256)
    thumbnailer.getThumbnail(file)

# Start the application
from src.ui.Application import TaggerApp

app = TaggerApp(file)
app.run(None)

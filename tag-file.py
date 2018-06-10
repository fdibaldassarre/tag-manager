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
from src.dao import filesDao
from src.System import addFile
from src.System import getRootRelativePath
from src.ui.Application import TaggerApp

filepath = args.file
name = getRootRelativePath(filepath)
# name = os.path.relpath(filepath, ConfigManager.getRoot())

file = filesDao.getByName(name)
if file is None:
    file = addFile(filepath)

# Start the application
app = TaggerApp(file)
app.run(None)

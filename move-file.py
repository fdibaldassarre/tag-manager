#!/usr/bin/env python3

import os
import sys
import argparse

parser = argparse.ArgumentParser(description="TM FileMover")
parser.add_argument('path', help='file to move')
parser.add_argument('--profile', default='default', help='profile name, default: default')
parser.add_argument('--debug', action='store_true', help='debug')

args = parser.parse_args()

path = args.path
profile = args.profile
debug = args.debug

if not os.path.exists(path):
    print("Missing file %d" % path)
    sys.exit(1)

# Configure the application
from src.Config import ConfigManager

profile_folder = os.path.join(os.environ['HOME'], ".config/tag-manager/" + profile)
ConfigManager.setup(profile_folder)
ConfigManager.debug = debug

# Start the application
from src.ui.Application import MoverApp

app = MoverApp(path)
app.run(None)

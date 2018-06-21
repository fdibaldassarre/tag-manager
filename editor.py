#!/usr/bin/env python3

import argparse
import os

from src.Config import ConfigManager

# Parse the command line argument
parser = argparse.ArgumentParser(description="Tag Editor")
parser.add_argument('--profile', default='default', help='profile name, default: default')
parser.add_argument('--debug', action='store_true', help='debug')

args = parser.parse_args()

# Configure the application
profile_folder = os.path.join(os.environ['HOME'], ".config/tag-manager/" + args.profile)
ConfigManager.setup(profile_folder)
ConfigManager.debug = args.debug

from src.ui.Application import EditorApp

app = EditorApp()
app.run(None)

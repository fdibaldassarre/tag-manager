#!/usr/bin/env python3

import os

path = os.path.abspath(__file__)
SRC_FOLDER = os.path.dirname(path)
MAIN_FOLDER = os.path.dirname(SRC_FOLDER)
RESOURCES_FOLDER = os.path.join(MAIN_FOLDER, "resources/")
GLADE_FOLDER = os.path.join(RESOURCES_FOLDER, "glade/")
ICONS_FOLDER = os.path.join(RESOURCES_FOLDER, "icons/")
CSS_FOLDER = os.path.join(RESOURCES_FOLDER, "css/")

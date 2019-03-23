#!/usr/bin/env python3

import argparse
import os

from src.Config import ConfigManager

# Parse the command line argument
parser = argparse.ArgumentParser(description="Tag Manager server")
parser.add_argument('profile_name', help='profile name')
parser.add_argument('--debug', action='store_true', help='debug')

args = parser.parse_args()

# Configure the application
profile_folder = os.path.join(os.environ['HOME'], ".config/tag-manager/" + args.profile_name)
ConfigManager.setup(profile_folder)
ConfigManager.debug = args.debug

from flask import Flask
from flask_restful import Api

from src.web.resources import Files
from src.web.resources import Tags
from src.web.resources import Metatags
from src.web.resources import FileTags
from src.web.resources import FileList

from src.Application import API_VERSION

PORT = ConfigManager.SERVER.getPort()
API_PREFIX = '/api/' + API_VERSION

app = Flask(__name__)
api = Api(app)

api.add_resource(Files,
                 API_PREFIX + '/files',
                 API_PREFIX + '/files/<int:eid>')
api.add_resource(Tags,
                 API_PREFIX + '/tags',
                 API_PREFIX + '/tags/<int:eid>')
api.add_resource(Metatags,
                 API_PREFIX + '/metatags',
                 API_PREFIX + '/metatags/<int:eid>')
api.add_resource(FileTags,
                 API_PREFIX + '/files/<int:fid>/tags',
                 API_PREFIX + '/files/<int:fid>/tags/<int:tid>',)
api.add_resource(FileList,
                 API_PREFIX + '/files/<int:fid>/list',)
app.run(host='0.0.0.0', port=PORT, debug=ConfigManager.debug)

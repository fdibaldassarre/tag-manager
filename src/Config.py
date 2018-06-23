#!/usr/bin/env python3

import os
from .Utils import json

CONFIG_UI = "ui"
CONFIG_SERVER = "server"

class ConfigSetting:

    def __init__(self, key, desc, default=None):
        self.key = key
        self.desc = desc
        self.default = default


class ChildConfig:

    symbol = None

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._sanityCheck()

    def _sanityCheck(self):
        pass

    def getConfig(self, setting):
        if setting.key in self.config_manager.settings[self.symbol]:
            return self.config_manager.settings[self.symbol][setting.key]
        else:
            return setting.default

    def setConfig(self, setting, newValue):
        oldValue = self.getConfig(setting)
        if newValue == oldValue:
            return
        # Set the new config
        self.config_manager.settings[self.symbol][setting.key] = newValue
        self.config_manager.save()


UI_METATAG = ConfigSetting("default-metatag", "Set metatags automatically selected when the browser starts")
UI_RANDOMIZE = ConfigSetting("randomize", "Show a set of random files when there are no search parameters set", False)
UI_FAST_FILTER = ConfigSetting("fast_filter", "Enable search as you type for the name filter in the browser",False)
UI_MOVER_METATAGS = ConfigSetting("mover-metatags", "List of metatags to add to the mover dialog")
UI_MOVER_TARGET_FOLDER = ConfigSetting("mover-target-folder", "Pattern of the target folder in the mover")
UI_MOVER_CUSTOM_PATTERN_KEYS = ConfigSetting("mover-custom-keys", "List of custom keys used in the target pattern")
UI_MOVER_OPEN_ON_TAG = ConfigSetting("mover-open-on-tag", "Open the file after moving", False)

class UISettings(ChildConfig):
    symbol = CONFIG_UI

    def getMetatagName(self):
        return self.getConfig(UI_METATAG)

    def getRandomize(self):
        return self.getConfig(UI_RANDOMIZE)

    def getMoverMetatags(self):
        return self.getConfig(UI_MOVER_METATAGS)

    def getFastFilter(self):
        return self.getConfig(UI_FAST_FILTER)

    def getMoverTargetFolder(self):
        return self.getConfig(UI_MOVER_TARGET_FOLDER)

    def getMoverCustomPatternKeys(self):
        return self.getConfig(UI_MOVER_CUSTOM_PATTERN_KEYS)

    def getMoverCustomPatternKeysEvaluator(self):
        return os.path.join(self.config_manager.profile_folder, 'modules/moverKeys.py')

    def getMoverDefaultValues(self):
        return os.path.join(self.config_manager.profile_folder, 'modules/moverDefaults.py')

    def getMoverOpenOnTag(self):
        return self.getConfig(UI_MOVER_OPEN_ON_TAG)


SERVER_PORT = ConfigSetting("port", "Port the API server listens on", 44659)

class ServerSettings(ChildConfig):
    symbol = CONFIG_SERVER

    def getPort(self):
        return self.getConfig(SERVER_PORT)

    def setPort(self, port):
        self.setConfig(SERVER_PORT, port)

MAIN_ROOT = 'root'

class _ConfigManager:

    profile_folder = None
    _settings_path = None
    settings = {}
    debug = False
    debugSql = False

    def loadChildConfigs(self):
        self.UI = UISettings(self)
        self.SERVER = ServerSettings(self)

    def setup(self, profile_folder):
        # Create profile folder
        self.profile_folder = profile_folder
        if not os.path.exists(profile_folder):
            os.makedirs(profile_folder)
        # Get configuration file
        self._settings_path = os.path.join(profile_folder, 'config.json')
        self.settings = self._loadSettings()
        # Sanity check
        self._check()
        # Load child configs
        self.loadChildConfigs()

    def _loadSettings(self):
        settings = {}
        if os.path.exists(self._settings_path):
            settings = json.load(open(self._settings_path))
        return settings

    def _check(self):
        edited = False
        # Check root setting
        if not MAIN_ROOT in self.settings:
            self.settings[MAIN_ROOT] = os.path.join(os.environ['HOME'], "TagManager/")
            edited = True
        # Check child configurations
        if not CONFIG_UI in self.settings:
            self.settings[CONFIG_UI] = {}
            edited = True
        if not CONFIG_SERVER in self.settings:
            self.settings[CONFIG_SERVER] = {}
            edited = True
        # Save
        if edited:
            self.save()

    def save(self):
        data = json.dumps(self.settings, indent=2)
        with open(self._settings_path, 'w') as hand:
            hand.write(data)

    def getRoot(self):
        return self.settings[MAIN_ROOT]

    def getProfileName(self):
        return os.path.basename(self.profile_folder)

    def getOverridesFolder(self):
        return os.path.join(self.profile_folder, "overrides/")

ConfigManager = _ConfigManager()

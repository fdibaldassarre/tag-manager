#!/usr/bin/env python3

import os
import shutil

from src.Config import ConfigManager
from src.Logging import createLogger
from src.System import addFile
from src.System import openFile
from src.Utils import loadModuleFromPath

from src.dao import filesDao
from src.dao import tagsDao
from src.dao import metatagsDao

from src.ui.common import ensureLoading
from src.ui.common import BaseController

from .MoverUI import MoverUI

UPDATE_PATH = 0

class MoverCtrl(BaseController):

    log = createLogger(__name__)

    def __init__(self, services, path):
        super().__init__(services)
        self.path = path
        self.loadConfiguration()
        self.ui = MoverUI(self)

    def loadConfiguration(self):
        self.metatags = {}
        metatags = ConfigManager.UI.getMoverMetatags()
        if metatags is not None:
            for name, selector in metatags.items():
                metatag = metatagsDao.getByName(name)
                self.metatags[metatag] = selector
        self.target_folder_pattern = ConfigManager.UI.getMoverTargetFolder()
        self.custom_target_keys = ConfigManager.UI.getMoverCustomPatternKeys()
        if self.custom_target_keys is not None:
            self.custom_target_keys_evaluator = self._loadCustomKeysEvaluator()
        self.default_values = self._getDefaultValues()

    def _loadCustomKeysEvaluator(self):
        module_path = ConfigManager.UI.getMoverCustomPatternKeysEvaluator()
        self.log.debug("Try to load %s" % module_path)
        custom = loadModuleFromPath("custom.keys", module_path)
        if custom is None:
            return None
        else:
            return custom.evaluate

    def _getDefaultValues(self):
        '''
            Get the default target name for the given path
            and some automatic tag.
        '''
        module_path =  ConfigManager.UI.getMoverDefaultValues()
        self.log.debug("Try to load %s" % module_path)
        if not os.path.exists(module_path):
            return None
        custom = loadModuleFromPath("custom.values", module_path)
        if custom is None:
            return None
        else:
            return custom.values(self.path)

    def setupUpdateEvents(self):
        '''
            Initialize the lists of the functions
            to call on update event.
        '''
        self.on_update = {}
        self.on_update[UPDATE_PATH] = []

    @ensureLoading
    def start(self):
        self.ui.show()

    def stop(self, close_ui=True):
        self.log.info("Stopping controller")
        if close_ui:
            self.log.info("Close ui")
            self.ui.close()
            return
        self.log.info("Ui closed, cleanup if necessary")

    def moveFileTo(self, folder, fname):
        '''
            Move the instance file to the given folder with
            the given name.

            :param str folder: target folder
            :param str fname: target name
            :return: target path
            :rtype: str
        '''
        target_base = os.path.join(folder, fname)
        while target_base.startswith('/'):
            target_base = target_base[1:]
        target = os.path.join(ConfigManager.getRoot(), target_base)
        self.log.info("Moving file from %s to %s" % (self.path, target))
        folder = os.path.dirname(target)
        if not os.path.isdir(folder):
            self.log.debug("Create folder %s" % folder)
            os.makedirs(folder)
        shutil.move(self.path, target)
        return target

    def addFile(self, path, tags):
        '''
            Open the tagger for a file.

            :param str path: Path of the file
            :param list of str: Tags names to add to the file
            :return: File added
            :rtype: dao.entities.Common.IFile
        '''
        self.log.info("Add file %s" % path)
        file = addFile(path)
        self.log.info("Added file #%d, name: %s, mime: %s" % (file.id, file.name, file.mime))
        # Apply tags
        session = tagsDao.openSession()
        filesDao.setSession(session)
        for tag_info in tags:
            name, metatag = tag_info
            self.log.info("Add tag %s" % name)
            tag = tagsDao.getByName(name)
            if tag is None:
                self.log.info("Create tag %s [%s]" % (name, metatag.name))
                tag = tagsDao.insert(name, metatag)
            file = filesDao.addTag(file, tag)
        tagsDao.closeSession(commit=True)
        filesDao.closeSession(commit=True)
        # Open file
        if ConfigManager.UI.getMoverOpenOnTag():
            openFile(file.name)
        self.services.getApplication().openTagger(file)
        return file

    # Update listeners
    def onUpdatePath(self, func):
        self.onUpdate(UPDATE_PATH, func)

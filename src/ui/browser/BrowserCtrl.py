#!/usr/bin/env python3

from src.Config import ConfigManager
from src.Logging import createLogger
from .BrowserUI import BrowserUI
from src.ui.common import BaseController

from src.dao import metatagsDao
from src.dao import tagsDao
from src.dao import filesDao

UPDATE_METATAGS = 0
UPDATE_TAGS = 1
UPDATE_FILES = 2
UPDATE_USED_TAGS = 3
UPDATE_AVAILABLE_METATAGS = 4
UPDATE_AVAILABLE_TAGS = 5

START_RANDOM_FILES = 9

class BrowserCtrl(BaseController):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.debug("Initialize")
        self.ui = BrowserUI(self)
        self._loaded = False
        self._setupUpdateEvents()
        self.log.debug("Done")


    def _setupUpdateEvents(self):
        '''
            Initialize the lists of the functions
            to call on update event.
        '''
        self.on_update = {}
        self.on_update[UPDATE_METATAGS] = []
        self.on_update[UPDATE_TAGS] = []
        self.on_update[UPDATE_FILES] = []
        self.on_update[UPDATE_USED_TAGS] = []
        self.on_update[UPDATE_AVAILABLE_METATAGS] = []
        self.on_update[UPDATE_AVAILABLE_TAGS] = []

    def start(self):
        '''
            Start the component.
        '''
        self.log.info("Start")
        if not self._loaded:
            self._load()
        self.ui.show()

    def _load(self):
        self.metatags = metatagsDao.getAll()
        self.tags = tagsDao.getAll()
        self.used_tags = []
        self.files = self._getFiles(self.used_tags)
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)
        self._loaded = True

    def _getRandomFiles(self):
        '''
            Get a list of random files.

            :return: A list of random files
            :rtype: list of dao.entities.Common.IFile
        '''
        return filesDao.getRandom(START_RANDOM_FILES)

    def _getAvailableTags(self, files):
        '''
            Get the tags useful to filter on the
            given files.

            :param list of IFile files: Files
            :return: list of tags
            :rtype: list of dao.entities.Common.ITag
        '''
        if len(self.used_tags) == 0 or len(files) == 0:
            # Get all the tags with at least one file tagged
            return tagsDao.getAllWithOneFileTagged()
        # Get the common tags
        common_tags = tagsDao.getCommonTags(files)
        # Remove the used tags
        available_tags = []
        used_ids = list(map(lambda t: t.id, self.used_tags))
        for tag in common_tags:
            if not tag.id in used_ids:
                available_tags.append(tag)
        return available_tags

    def _getAvailableMetatags(self, tags):
        metatags = {}
        for tag in tags:
            if not tag.metatag.id in metatags:
                metatags[tag.metatag.id] = tag.metatag
        return sorted(list(metatags.values()), key=lambda m: m.name.lower())

    def _getFiles(self, tags):
        if len(tags) == 0:
            if ConfigManager.UI.getRandomize():
                return self._getRandomFiles()
            else:
                return []
        return filesDao.getByNameAndTags(tags=tags)

    def addTag(self, tag):
        self.used_tags.append(tag)
        self.files = self._getFiles(self.used_tags)
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)
        # Trigger
        self._trigger(UPDATE_USED_TAGS)
        self._trigger(UPDATE_FILES)
        self._trigger(UPDATE_AVAILABLE_METATAGS)
        self._trigger(UPDATE_AVAILABLE_TAGS)


    def removeTag(self, tag):
        self.used_tags.remove(tag)
        self.files = self._getFiles(self.used_tags)
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)
        # Trigger
        self._trigger(UPDATE_USED_TAGS)
        self._trigger(UPDATE_FILES)
        self._trigger(UPDATE_AVAILABLE_METATAGS)
        self._trigger(UPDATE_AVAILABLE_TAGS)

    # Update listeners
    def onUpdateMetags(self, func):
        self.onUpdate(UPDATE_METATAGS, func)

    def onUpdateTags(self, func):
        self.onUpdate(UPDATE_TAGS, func)

    def onUpdateFiles(self, func):
        self.onUpdate(UPDATE_FILES, func)

    def onUpdateUsedTags(self, func):
        self.onUpdate(UPDATE_USED_TAGS, func)

    def onUpdateAvailableMetatags(self, func):
        self.onUpdate(UPDATE_AVAILABLE_METATAGS, func)

    def onUpdateAvailableTags(self, func):
        self.onUpdate(UPDATE_AVAILABLE_TAGS, func)

    def onUpdate(self, event, func):
        self.on_update[event].append(func)
        func()

    def _trigger(self, event):
        for f in self.on_update[event]:
            f()

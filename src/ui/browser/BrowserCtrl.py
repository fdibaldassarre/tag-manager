#!/usr/bin/env python3

from src.Config import ConfigManager
from src.Logging import createLogger

from src.ui.common import ensureLoading
from src.ui.common import BaseController

from src.dao import metatagsDao
from src.dao import tagsDao
from src.dao import filesDao

from src import System

from .BrowserUI import BrowserUI


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
        self.log.debug("Done")

    def setupUpdateEvents(self):
        super().setupUpdateEvents()
        self.on_update[UPDATE_METATAGS] = []
        self.on_update[UPDATE_TAGS] = []
        self.on_update[UPDATE_FILES] = []
        self.on_update[UPDATE_USED_TAGS] = []
        self.on_update[UPDATE_AVAILABLE_METATAGS] = []
        self.on_update[UPDATE_AVAILABLE_TAGS] = []

    @ensureLoading
    def start(self):
        self.ui.show()

    def load(self):
        self.metatags = metatagsDao.getAll()
        self.tags = tagsDao.getAll()
        self.used_tags = []
        self.name_filter = None
        self.files = self._getFiles(self.used_tags)
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)

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
        common_tags = tagsDao.getRelatedTags(self.used_tags)
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

    def _getFiles(self, tags, name=None):
        if len(tags) == 0 and name is None:
            if ConfigManager.UI.getRandomize():
                return self._getRandomFiles()
            else:
                return []
        return filesDao.getByNameAndTags(name=name, tags=tags)

    def addTag(self, tag):
        self.used_tags.append(tag)
        self._searchFiles()

    def removeTag(self, tag):
        self.used_tags.remove(tag)
        self._searchFiles()

    def addNameFilter(self, name):
        if name is None:
            self.name_filter = None
        else:
            self.name_filter = '%'.join(name.strip().split())
            if self.name_filter == '':
                self.name_filter = None
            else:
                self.name_filter = '%' + self.name_filter +'%'
        self._searchFiles()

    def _searchFiles(self):
        self.files = self._getFiles(self.used_tags, self.name_filter)
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)
        # Trigger
        self.trigger(UPDATE_USED_TAGS)
        self.trigger(UPDATE_FILES)
        self.trigger(UPDATE_AVAILABLE_METATAGS)
        self.trigger(UPDATE_AVAILABLE_TAGS)


    def openTagger(self, file):
        tagger_ctrl = self.services.getApplication().openTagger(file)

    def removeFile(self, file):
        '''
            Remove a file from database and filesystem.

            :param dao.entities.IFileLazy file: File to remove
        '''
        # Remove the file from the system
        self.log.info("Remove file: %s" % file.name)
        System.removeFile(file)
        self.log.debug("Remove from controller files list")
        # Remove file from the list
        for cfile in self.files:
            if cfile.id == file.id:
                self.files.remove(cfile)
                break
        # Update tags and metatags
        self.log.debug("Update available tags and metatags")
        self.available_tags = self._getAvailableTags(self.files)
        self.available_metatags = self._getAvailableMetatags(self.available_tags)
        self.trigger(UPDATE_FILES)
        self.trigger(UPDATE_AVAILABLE_METATAGS)
        self.trigger(UPDATE_AVAILABLE_TAGS)

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

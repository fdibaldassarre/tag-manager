#!/usr/bin/env python3

from src.Logging import createLogger
from .TaggerUI import TaggerUI
from src.ui.common import BaseController

from src.dao import metatagsDao
from src.dao import tagsDao
from src.dao import filesDao

UPDATE_METATAGS = 0
UPDATE_TAGS = 1
UPDATE_FILE_TAG = 2

class TaggerCtrl(BaseController):

    log = createLogger(__name__)

    def __init__(self, services, file):
        super().__init__(services)
        self.ui = TaggerUI(self)
        self.file = file
        self._setupUpdateEvents()
        self.log.debug("Initialized")


    def _setupUpdateEvents(self):
        '''
            Initialize the lists of the functions
            to call on update event.
        '''
        self.on_update = {}
        self.on_update[UPDATE_METATAGS] = []
        self.on_update[UPDATE_TAGS] = []
        self.on_update[UPDATE_FILE_TAG] = []

    def start(self):
        '''
            Start the component.
        '''
        self._load()
        self.ui.show()

    def stop(self, close_ui=True):
        self.log.info("Stopping controller")
        if close_ui:
            self.log.info("Close ui")
            self.ui.close()
            return
        self.log.info("Ui closed, cleanup if necessary")
        # TODO

    def _load(self):
        self.metatags = metatagsDao.getAll()
        self.tags = tagsDao.getAll()

    def fileHasTag(self, tag_id):
        '''
            Check if the file has the given tag.

            :param int tag_id: Tag id
            :return: True if the file has this tag, False otherwise
            :rtype: bool
        '''
        in_tags = False
        for tag in self.file.tags:
            if tag.id == tag_id:
                in_tags = True
                break
        return in_tags

    def addTagToFile(self, tag_id):
        if self.fileHasTag(tag_id):
            return
        tag = tagsDao.getById(tag_id)
        self.file = filesDao.addTag(self.file, tag)
        self._trigger(UPDATE_FILE_TAG, (tag, True))

    def removeTagFromFile(self, tag_id):
        if not self.fileHasTag(tag_id):
            return
        tag = tagsDao.getById(tag_id)
        self.file = filesDao.removeTag(self.file, tag)
        self._trigger(UPDATE_FILE_TAG, (tag, False))

    def createMetatag(self, name):
        metatag = metatagsDao.insert(name)
        self.metatags = metatagsDao.getAll()
        self._trigger(UPDATE_METATAGS)
        return metatag

    def createTag(self, name, metatag):
        tag = tagsDao.insert(name, metatag)
        self.tags = tagsDao.getAll()
        self._trigger(UPDATE_TAGS)
        return tag

    # Update listeners
    def onUpdateMetatags(self, func):
        self.onUpdate(UPDATE_METATAGS, func)

    def onUpdateTags(self, func):
        self.onUpdate(UPDATE_TAGS, func)

    def onUpdateFileTag(self, func):
        self.onUpdate(UPDATE_FILE_TAG, func)

    def onUpdate(self, event, func):
        self.on_update[event].append(func)
        func()

    def _trigger(self, event, data=None):
        for f in self.on_update[event]:
            if data is None:
                f()
            else:
                f(*data)

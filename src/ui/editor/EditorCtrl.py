#!/usr/bin/env python3

from src.Logging import createLogger

from src.ui.common import ensureLoading
from src.ui.common import BaseController

from src.dao import metatagsDao
from src.dao import tagsDao

from .EditorUI import EditorUI

UPDATE_METATAGS = 0
UPDATE_TAGS = 1

class EditorCtrl(BaseController):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = EditorUI(self)

    @ensureLoading
    def start(self):
        self.ui.show()

    def stop(self):
        self.ui.close()

    def load(self):
        self.metatags = metatagsDao.getAll()
        self.tags = tagsDao.getAll()

    def setupUpdateEvents(self):
        super().setupUpdateEvents()
        self.on_update[UPDATE_METATAGS] = []
        self.on_update[UPDATE_TAGS] = []

    def _updateTags(self):
        self.tags = tagsDao.getAll()
        self.trigger(UPDATE_TAGS)

    def _updateMetatags(self):
        self.metatags = metatagsDao.getAll()
        self.trigger(UPDATE_METATAGS)

    # Public methods
    def addTag(self, name, metatag):
        self.log.info("Add tag %s with metatag %s" % (name, metatag.name))
        try:
            tagsDao.insert(name, metatag)
        except Exception:
            return False
        # Update
        self._updateTags()
        return True


    def addMetatag(self, name):
        self.log.info("Add metatag %s" % name)
        try:
            metatagsDao.insert(name)
        except Exception:
            return False
        # Update
        self._updateMetatags()
        return True

    def deleteTag(self, tag):
        self.log.info("Delete tag %s" % tag.name)
        try:
            tagsDao.delete(tag)
        except Exception:
            return False
        # Update
        self._updateTags()
        return True


    def deleteMetatag(self, metatag):
        self.log.info("Delete metatag %s" % metatag.name)
        try:
            metatagsDao.delete(metatag)
        except Exception:
            return False
        # Update
        self._updateMetatags()
        return True

    def editTag(self, tag, new_name, new_metatag):
        self.log.info("Edit tag %s" % tag.name)
        self.log.info("New name %s, new metatag: %s" % (new_name, new_metatag.name))
        try:
            tagsDao.update(tag, new_name, new_metatag)
        except Exception:
            return False
        # Update
        self._updateTags()
        return True

    def editMetatag(self, metatag, new_name):
        self.log.info("Edit metatag %s" % metatag.name)
        self.log.info("New name %s" % new_name)
        try:
            metatagsDao.update(metatag, name=new_name)
        except Exception:
            return False
        # Update
        self._updateMetatags()
        self._updateTags()
        return True

    # Update listeners
    def onUpdateMetatags(self, func):
        self.onUpdate(UPDATE_METATAGS, func)

    def onUpdateTags(self, func):
        self.onUpdate(UPDATE_TAGS, func)

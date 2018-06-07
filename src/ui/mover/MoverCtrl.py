#!/usr/bin/env python3

from src.Config import ConfigManager
from src.Logging import createLogger

from src.ui.common import ensureLoading
from src.ui.common import BaseController

from .MoverUI import MoverUI

UPDATE_PATH = 0

class MoverCtrl(BaseController):

    log = createLogger(__name__)

    def __init__(self, services, path):
        super().__init__(services)
        self.path = path
        self.ui = MoverUI(self)

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
        # TODO

    # Update listeners
    def onUpdatePath(self, func):
        self.onUpdate(UPDATE_PATH, func)

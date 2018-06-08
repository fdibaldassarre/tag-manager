#!/usr/bin/env python3

import os

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

from src.Places import GLADE_FOLDER
from src.Logging import createLogger
from src.Config import ConfigManager

from src.ui.common import BaseInterface

class MoverUI(BaseInterface):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None
        self.log.debug("Done")

    def _build(self):
        '''
            Build the interface.
        '''
        self.builder = Gtk.Builder()
        ui_file = os.path.join(GLADE_FOLDER, 'AddFile.glade')
        self.builder.add_from_file(ui_file)
        self.window = self.builder.get_object('AMMainWindow')
        self.window.set_title("Move file to profile: %s" % ConfigManager.getProfileName())
        app = self.ctrl.services.getApplication()
        app.add_window(self.window)
        # Register the update events
        self.ctrl.onUpdatePath(self.onPathChange)

    def show(self):
        if self.window is None:
            self._build()
        self.window.show()

    def onPathChange(self):
        # Set basename
        basename = os.path.basename(self.ctrl.path)
        label = self.builder.get_object('AMLabelBasename')
        label.set_text(basename)
        entry = self.builder.get_object('AMEntryName')
        entry.set_text(basename)

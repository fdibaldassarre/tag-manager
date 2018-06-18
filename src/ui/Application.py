#!/usr/bin/env python3

import os

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

from src.Config import ConfigManager
from src.Places import ICONS_FOLDER
from src.Places import CSS_FOLDER

from .browser.BrowserCtrl import BrowserCtrl
from .tagger.TaggerCtrl import TaggerCtrl
from .mover.MoverCtrl import MoverCtrl

class ServiceManager:

    def __init__(self, app):
        self.app = app

    def getApplication(self):
        return self.app

class TagManagerApp(Gtk.Application):

    def __init__(self):
        super().__init__(application_id="fdibaldassarre.tagmanager")
        Gdk.set_program_class("Tag Manager")
        self.services = ServiceManager(self)
        self._loadControllers()
        self._loadCssProvider()
        self._loadIcon()
        self.connect("activate", self.do_activate)

    def _loadControllers(self):
        self.browser = BrowserCtrl(self.services)

    def _loadIcon(self):
        self.icon_path = os.path.join(ConfigManager.getOverridesFolder(), "icon.png")
        if not os.path.exists(self.icon_path):
            self.icon_path = os.path.join(ICONS_FOLDER, "icon.png")

    def do_activate(self, data=None):
        self.browser.start()

    def openTagger(self, file):
        '''
            Open the tagger for a file.

            :param dao.entities.common.IFile file: File to tag
            :return: Tagger controller
            :rtype: ui.tagger.TaggerCtrl
        '''
        self.tagger = TaggerCtrl(self.services, file)
        self.tagger.start()
        return self.tagger

    def _loadCssProvider(self):
        display = Gdk.Display.get_default()
        screen = Gdk.Display.get_default_screen(display)
        provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        # TODO: load file
        #css_file = os.path.join(CSS_FOLDER, 'TagManager.css')
        #provider.load_from_path(css_file)

class TaggerApp(TagManagerApp):

    def __init__(self, file):
        super().__init__()
        self.tagger = TaggerCtrl(self.services, file)

    def do_activate(self, data=None):
        self.tagger.start()

class MoverApp(TagManagerApp):

    def __init__(self, path):
        '''
            Initialize.

            :param str path: Path of the file to move to the root folder
        '''
        super().__init__()
        self.mover = MoverCtrl(self.services, path)

    def do_activate(self, data=None):
        self.mover.start()

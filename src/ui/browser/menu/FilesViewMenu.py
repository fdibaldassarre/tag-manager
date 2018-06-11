#!/usr/bin/env python3

from gi.repository import Gtk
from gi.repository import Gio

class FilesViewMenuFactory():

    def __init__(self, openFolder, openTagger, removeFile):
        self.name = 'filesview'
        self.openFolder = openFolder
        self.openTagger = openTagger
        self.removeFile = removeFile

    def _createActionGroup(self):
        '''
            Create the action group for the
            files view.

            :return: The files view action group
            :rtype: Gio.SimpleActionGroup
        '''
        group = Gio.SimpleActionGroup()
        open_folder = Gio.SimpleAction.new("open_folder")
        open_folder.connect("activate", self.openFolder)
        tag_file = Gio.SimpleAction.new("tag_file")
        tag_file.connect("activate", self.openTagger)
        remove_file = Gio.SimpleAction.new("remove_file")
        remove_file.connect("activate", self.removeFile)
        group.add_action(open_folder)
        group.add_action(tag_file)
        group.add_action(remove_file)
        return group

    def _createMenuModel(self):
        menu = Gio.Menu()
        ## open
        open_action = Gio.MenuItem.new("Open Folder", self.name + '.open_folder')
        open_icon = Gio.ThemedIcon.new('gtk-open')
        open_action.set_icon(open_icon)
        menu.insert_item(0, open_action)
        ## edit
        edit = Gio.MenuItem.new("Edit Tags", self.name +  '.tag_file')
        edit_icon = Gio.ThemedIcon.new('gtk-edit')
        edit.set_icon(edit_icon)
        menu.insert_item(1, edit)
        ## remove
        remove = Gio.MenuItem.new("Remove File", self.name + '.remove_file')
        remove_icon = Gio.ThemedIcon.new('gtk-delete')
        remove.set_icon(remove_icon)
        menu.insert_item(2, remove)
        return menu

    def createGtkMenu(self):
        # Create menu model
        model = self._createMenuModel()
        # Create menu
        menu = Gtk.Menu.new_from_model(model)
        ## Attach action group
        action_group = self._createActionGroup()
        menu.insert_action_group(self.name, action_group)
        return menu

def new(*args, **kargs):
    factory = FilesViewMenuFactory(*args, **kargs)
    return factory.createGtkMenu()

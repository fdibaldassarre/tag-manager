#!/usr/bin/env python3

import os

from gi.repository import Gtk

from src.Logging import createLogger
from src.Places import GLADE_FOLDER

from src.ui.common import BaseInterface

class EditorUI(BaseInterface):

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
        ui_file = os.path.join(GLADE_FOLDER, 'Editor.glade')
        self.builder.add_from_file(ui_file)
        self.window = self.builder.get_object('Main')
        self.window.resize(400, 100)
        # Register window
        app = self.ctrl.services.getApplication()
        app.add_window(self.window)
        # Register the update events
        self.ctrl.onUpdateMetatags(self.onUpdateMetatags)
        self.ctrl.onUpdateTags(self.onUpdateTags)
        # Connect signals
        self.builder.connect_signals(self)

    def show(self):
        if self.window is None:
            self._build()
        self.window.show()

    def close(self):
        self.window.close()

    def setParent(self, window):
        self.window.set_transient_for(window)

    # LISTENERS
    def _updateMetatagSelector(self, selector):
        selector.remove_all()
        for metatag in self.ctrl.metatags:
            selector.append_text(metatag.name)

    def _updateTagSelector(self, selector):
        selector.remove_all()
        for tag in self.ctrl.tags:
            selector.append_text(tag.name)

    def onUpdateMetatags(self):
        selector_ids = ["AddTagMetatagSelect", "EditTagMetatagSelect", "EditMetatagSelect", "DeleteMetatagSelect"]
        for sid in selector_ids:
            selector = self.builder.get_object(sid)
            self._updateMetatagSelector(selector)

    def onUpdateTags(self):
        selector_ids = ["EditTagSelect", "DeleteTagSelect"]
        for sid in selector_ids:
            selector = self.builder.get_object(sid)
            self._updateTagSelector(selector)

    # SIGNALS
    def _getWidgetText(self, selector_id):
        label = self.builder.get_object(selector_id)
        name = label.get_text()
        return name.strip()

    def _getSelectorElement(self, selector_id, model):
        selector = self.builder.get_object(selector_id)
        active = selector.get_active()
        if active == -1:
            return None
        else:
            return model[active]

    def _resetLabel(self, selector_id):
        label = self.builder.get_object(selector_id)
        label.set_text("")

    def _resetSelector(self, selector_id):
        selector = self.builder.get_object(selector_id)
        selector.set_active(-1)

    def onClose(self, widget):
        self.ctrl.stop()

    def onAddMetatag(self, widget):
        name = self._getWidgetText("AddMetatagName")
        if len(name) == 0:
            return
        success = self.ctrl.addMetatag(name)
        if success:
            # Reset
            self._resetLabel("AddMetatagName")
        else:
            self.createMessageDialog("Error", "Could not add the metatag %s" % name)

    def onAddTag(self, widget):
        name = self._getWidgetText("AddTagName")
        metatag = self._getSelectorElement("AddTagMetatagSelect", self.ctrl.metatags)
        if len(name) == 0 or metatag is None:
            return
        success = self.ctrl.addTag(name, metatag)
        if success:
            # Reset
            self._resetLabel("AddTagName")
            self._resetSelector("AddTagMetatagSelect")
        else:
            self.createMessageDialog("Error", "Could not add the tag %s" % name)

    def onEditMetatag(self, widget):
        metatag = self._getSelectorElement("EditMetatagSelect", self.ctrl.metatags)
        new_name = self._getWidgetText("EditMetatagName")
        if metatag is None or len(new_name) == 0:
            return
        success = self.ctrl.editMetatag(metatag, new_name)
        if success:
            # Reset
            self._resetSelector("EditMetatagSelect")
            self._resetLabel("EditMetatagName")
        else:
            self.createMessageDialog("Error", "Could not rename the metatag %s" % metatag.name)

    def onEditTag(self, widget):
        tag = self._getSelectorElement("EditTagSelect", self.ctrl.tags)
        new_name = self._getWidgetText("EditTagName")
        new_metatag = self._getSelectorElement("EditTagMetatagSelect", self.ctrl.metatags)
        if tag is None or len(new_name) == 0 or new_metatag is None:
            return
        success = self.ctrl.editTag(tag, new_name, new_metatag)
        if success:
            # Reset
            self._resetSelector("EditTagSelect")
            self._resetLabel("EditTagName")
            self._resetSelector("EditTagMetatagSelect")
        else:
            self.createMessageDialog("Error", "Could not edit the tag %s" % tag.name)

    def onDeleteMetatag(self, widget):
        metatag = self._getSelectorElement("DeleteMetatagSelect", self.ctrl.metatags)
        if metatag is None:
            return
        onConfirm = lambda : self.onDeleteMetatagReal(metatag)
        dialog = self.createConfirmationDialog("Confirm deletion",
                                               "Do you want to delete the metatag %s ?" % metatag.name,
                                               onConfirm)

    def onDeleteTag(self, widget):
        tag = self._getSelectorElement("DeleteTagSelect", self.ctrl.tags)
        if tag is None:
            return
        onConfirm = lambda : self.onDeleteTagReal(tag)
        dialog = self.createConfirmationDialog("Confirm deletion",
                                               "Do you want to delete the tag %s ?" % tag.name,
                                               onConfirm)

    def onDeleteMetatagReal(self, metatag):
        success = self.ctrl.deleteMetatag(metatag)
        if success:
            self._resetSelector("DeleteMetatagSelect")
        else:
            self.createMessageDialog("Error", "Could not delete metatag %s" % metatag.name)

    def onDeleteTagReal(self, tag):
        success = self.ctrl.deleteTag(tag)
        if success:
            self._resetSelector("DeleteTagSelect")
        else:
            self.createMessageDialog("Error", "Could not delete tag %s" % tag.name)

    def onMetatagChanged(self, widget):
        metatag = self._getSelectorElement("EditMetatagSelect", self.ctrl.metatags)
        if metatag is None:
            return
        label = self.builder.get_object("EditMetatagName")
        label.set_text(metatag.name)

    def onTagChanged(self, widget):
        tag = self._getSelectorElement("EditTagSelect", self.ctrl.tags)
        if tag is None:
            return
        # Set name
        label = self.builder.get_object("EditTagName")
        label.set_text(tag.name)
        # Set metatag
        active_index = -1
        for index, metatag in enumerate(self.ctrl.metatags):
            if metatag.name == tag.metatag.name:
                active_index = index
                break
        selector = self.builder.get_object("EditTagMetatagSelect")
        selector.set_active(active_index)
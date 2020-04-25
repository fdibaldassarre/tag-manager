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
        self._buildTagsAutocompleteBox()
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

    def _buildTagsAutocompleteBox(self):
        self.tags_store = Gtk.ListStore(int, str, int)
        edit_entry = self.builder.get_object("EditTagSelect")
        self._buildAutocompletionBox(edit_entry, self.onTagChanged)
        delete_entry = self.builder.get_object("DeleteTagSelect")
        self._buildAutocompletionBox(delete_entry)

    def _buildAutocompletionBox(self, search_entry, on_match_selected=None):
        '''
            Set the autocompletion behaviour.
        '''
        completion = Gtk.EntryCompletion.new()
        # Set model
        completion.set_model(self.tags_store)
        completion.set_text_column(1)
        # Settings
        completion.set_inline_completion(False)
        completion.set_popup_completion(True)
        completion.set_popup_set_width(True)
        completion.set_popup_single_match(True)
        completion.set_inline_selection(True)
        if on_match_selected is not None:
            completion.connect("match-selected", on_match_selected)
        # Add to entry
        search_entry.set_completion(completion)

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

    def onUpdateMetatags(self):
        selector_ids = ["AddTagMetatagSelect", "EditTagMetatagSelect", "EditMetatagSelect", "DeleteMetatagSelect"]
        for sid in selector_ids:
            selector = self.builder.get_object(sid)
            self._updateMetatagSelector(selector)

    def onUpdateTags(self):
        self.tags_store.clear()
        tags_store = [[index, tag, tag.name.lower()] for index, tag in enumerate(self.ctrl.tags)]
        sorted_tags = sorted(tags_store, key=lambda element: element[2])
        for position, tag, _ in sorted_tags:
            self.tags_store.append([tag.id, tag.name, position])

    # SELECTORS GETTERS
    def _getSelectedTag(self, widget):
        '''
            Return the tag selected in the widget.
            Widget should extend Gtk.Entry.
        '''
        tag_name = widget.get_text()
        matched_tags = list(filter(lambda t: t.name == tag_name, self.ctrl.tags))
        if(len(matched_tags) == 0):
            return None
        else:
            return matched_tags[0]

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
        tag_widget = self.builder.get_object("EditTagSelect")
        tag = self._getSelectedTag(tag_widget)
        new_name = self._getWidgetText("EditTagName")
        new_metatag = self._getSelectorElement("EditTagMetatagSelect", self.ctrl.metatags)
        if tag is None or len(new_name) == 0 or new_metatag is None:
            return
        success = self.ctrl.editTag(tag, new_name, new_metatag)
        if success:
            # Reset
            self._resetLabel("EditTagSelect")
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
        tag_widget = self.builder.get_object("DeleteTagSelect")
        tag = self._getSelectedTag(tag_widget)
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
            self._resetLabel("DeleteTagSelect")
        else:
            self.createMessageDialog("Error", "Could not delete tag %s" % tag.name)

    def onMetatagChanged(self, widget):
        metatag = self._getSelectorElement("EditMetatagSelect", self.ctrl.metatags)
        if metatag is None:
            return
        label = self.builder.get_object("EditMetatagName")
        label.set_text(metatag.name)

    def onTagChanged(self, widget, model, path):
        _, _, index = model[path]
        tag = self.ctrl.tags[index]
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

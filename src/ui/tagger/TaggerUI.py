#!/usr/bin/env python3

import os

from gi.repository import Gtk
from gi.repository.GObject import GType
from gi.repository.GdkPixbuf import Pixbuf

from src.Logging import createLogger
from src.Config import ConfigManager
from src.Places import GLADE_FOLDER
from src.Places import ICONS_FOLDER
from src.ui.common import BaseInterface
from src.ui.Utils import inhibitSignals
from src.ui.Utils import withInhibit
from src.System import openFile

ICON_SIZE = 256

FILES_LIMIT = 100 #9

PIXBUF_MISSING = Gtk.IconTheme.get_default().load_icon(Gtk.STOCK_MISSING_IMAGE, ICON_SIZE, 0)

class TaggerUI(BaseInterface):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None

    def _build(self):
        '''
            Build the interface. Should be called only once.
        '''
        self.log.info("Building...")
        self.builder = Gtk.Builder()
        ui_file = os.path.join(GLADE_FOLDER, 'Tagger.glade')
        self.builder.add_from_file(ui_file)
        # Create main window
        self.window = self.builder.get_object("TagFile")
        self.window.resize(400, 600)
        # Set window title
        fname = os.path.basename(self.ctrl.file.name)
        self.window.set_title("Tag: " + fname)
        # Register main window
        app = self.ctrl.services.getApplication()
        self.window.set_icon_from_file(app.icon_path)
        app.add_window(self.window)
        # Setup ui variables
        self.tags_store = Gtk.ListStore(int, str, int)
        self.metatag_tagstore = {}
        self.metatag_view = {}
        self.metatag_selected = None
        self.tag_selected = None
        # Build interface
        self._buildAutocompletionBox()
        # Register the create events
        self.ctrl.onUpdateMetatags(self.updateMetatagList)
        self.ctrl.onUpdateTags(self.updateTagsList)
        self.ctrl.onUpdateTags(self.updateTagsGrids)
        self.ctrl.onUpdateFileTag(self.onFileTagChanged)
        # Add a signal handler
        self.builder.connect_signals(self)

    def show(self):
        '''
            Show the main window.
        '''
        if self.window is None:
            self._build()
        self.window.show()

    def _buildAutocompletionBox(self):
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
        # Connect
        completion.connect("match-selected", self.onTagCompletionSelected)
        # Add to entry
        sentry = self.builder.get_object("TFSearchEntry")
        sentry.set_completion(completion)

    def _buildTagsGridFor(self, metatag):
        '''
            Build the tags grid for the given metatag

            :param dao.Common.IMetatag metatag
            :return: List of tags associated
            :rtype: Gtk.ListStore
        '''
        self.metatag_tagstore[metatag.id] = Gtk.ListStore(int, str, bool)
        # Treeview
        treeview = Gtk.TreeView(model=self.metatag_tagstore[metatag.id])
        treeview.set_hexpand(True)
        # Cell renderer
        renderer_toggle = Gtk.CellRendererToggle()
        column_toggle = Gtk.TreeViewColumn("", renderer_toggle, active = 2)
        renderer_toggle.connect("toggled", self.onTagToggled, self.metatag_tagstore[metatag.id])
        treeview.append_column(column_toggle)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Tag", renderer_text, text=1)
        treeview.append_column(column_text)
        treeview.set_search_column(1)
        # Add scrolled window
        scrolled_view = Gtk.ScrolledWindow()
        scrolled_view.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_view.add(treeview)
        scrolled_view.set_vexpand(True)
        self.metatag_view[metatag.id] = scrolled_view
        # Add to the main window
        all_tags_grid = self.builder.get_object("TFTagsBox")
        all_tags_grid.add(scrolled_view)
        return self.metatag_tagstore[metatag.id]

    @inhibitSignals
    def updateMetatagList(self):
        '''
            Update the metatag selectors.
        '''
        # Grid selector
        selector = self.builder.get_object("TFCategorySelector")
        selector.remove_all()
        for metatag in self.ctrl.metatags:
            selector.append_text(metatag.name)
        # Add tag selector
        add_selector = self.builder.get_object("TFAddTagCategory")
        add_selector.remove_all()
        for metatag in self.ctrl.metatags:
            add_selector.append_text(metatag.name)
        # Tags grids
        for metatag in self.ctrl.metatags:
            if not metatag.id in self.metatag_tagstore:
                self._buildTagsGridFor(metatag)
        if len(self.ctrl.metatags) > 0:
            selector.set_active(0)
            add_selector.set_active(0)
            self._setMetatag(self.ctrl.metatags[0])

    def updateTagsList(self):
        '''
            Update the tags list.
        '''
        self.tags_store.clear()
        sorted_tags = sorted(self.ctrl.tags, key=lambda tag: tag.name.lower())
        for tag in sorted_tags:
            self.tags_store.append([tag.id, tag.name, tag.metatag.id])

    def updateTagsGrids(self):
        '''
            Update the tags grids.
        '''
        # Clear all
        for metatag in self.ctrl.metatags:
            if metatag.id in self.metatag_tagstore:
                self.metatag_tagstore[metatag.id].clear()
        # Populate
        for tag in self.ctrl.tags:
            metatag = tag.metatag
            if metatag.id in self.metatag_tagstore:
                self.metatag_tagstore[metatag.id].append([tag.id, tag.name, self.ctrl.fileHasTag(tag.id)])

    def _setMetatag(self, metatag):
        '''
            Set the metatag in the selector.
        '''
        # Hide old
        if self.metatag_selected is not None:
            self.metatag_view[self.metatag_selected.id].hide()
        # Set and show new
        self.metatag_selected = metatag
        self.metatag_view[self.metatag_selected.id].show_all()

    def _setTagToFile(self, tag_id, add):
        '''
            Toggle a tag.

            :param int tag_id: tag id
            :param bool add: True if I should add the tag, False otherwise
        '''
        if add:
            self.ctrl.addTagToFile(tag_id)
        else:
            self.ctrl.removeTagFromFile(tag_id)

    def onFileTagChanged(self, tag=None, added=True):
        '''
            When a tag has been added or removed from a file
        '''
        if tag is None:
            return
        # Edit all the list_store
        if tag.metatag.id in self.metatag_tagstore:
            store = self.metatag_tagstore[tag.metatag.id]
            for i in range(len(store)):
                tag_id, _, _ = store[i]
                if tag_id == tag.id:
                    store[i][-1] = added
                    break
        # Edit the tag_selected button if present
        if self.tag_selected == tag.id:
            btn = self.builder.get_object('TFSearchTagValue')
            btn.set_active(added)

    def onCreateMetatag(self, widget):
        entry = self.builder.get_object("TFAddCategoryName")
        name = entry.get_text().strip()
        if len(name) > 0:
            self.ctrl.createMetatag(name)

    def onCreateTag(self, widget):
        entry = self.builder.get_object("TFAddTagName")
        name = entry.get_text().strip()
        if len(name) == 0:
            return True
        m_selector = self.builder.get_object("TFAddTagCategory")
        metatag = self.ctrl.metatags[m_selector.get_active()]
        tag = self.ctrl.createTag(name, metatag)
        self.ctrl.addTagToFile(tag.id)

    # SIGNALS
    def onTagCompletionSelected(self, widget, model, path):
        '''
            On tag selected from autocompletion.
        '''
        tag_id, tag_name, metatag_id = model[path]
        self.tag_selected = tag_id
        # Show name
        label = self.builder.get_object("TFSearchTagName")
        label.set_text(tag_name)
        label.show()
        # Clear entry
        entry = self.builder.get_object("TFSearchEntry")
        entry.set_text("")
        # Set/Unset
        btn = self.builder.get_object('TFSearchTagValue')
        btn.set_active(True)
        btn.show()
        self._setTagToFile(self.tag_selected, True)
        # Return True otherwise the match-selected default behaviour
        # overwrites the text inside the entry
        # see: https://developer.gnome.org/gtk3/stable/GtkEntryCompletion.html#GtkEntryCompletion-match-selected
        return True

    @withInhibit
    def onMetatagChange(self, widget):
        '''
            On metagag changed event.
        '''
        index = widget.get_active()
        self._setMetatag(self.ctrl.metatags[index])

    def onTagToggled(self, widget, path=None, model=None):
        '''
            On tag toggled (from the autocompletion box
            or tag grid).
        '''
        if model is None:
            tag = self.tag_selected
            add = widget.get_active()
        else:
            tag = model[path][0]
            add = not model[path][2]
        if tag is None:
            return
        self._setTagToFile(tag, add)
        return True

    def onCloseClicked(self, widget):
        self.log.info("Stop the controller")
        self.ctrl.stop()

    def onDestroy(self, widget):
        self.log.info("Stop the controller")
        self.ctrl.stop(False)

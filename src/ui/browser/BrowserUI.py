#!/usr/bin/env python3

import os

from gi.repository import Gtk
from gi.repository import Gdk
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

from .menu import FilesViewMenu

ICON_SIZE = 256

FILES_LIMIT = 100 #9

PIXBUF_MISSING = Gtk.IconTheme.get_default().load_icon(Gtk.STOCK_MISSING_IMAGE, ICON_SIZE, 0)

class BrowserUI(BaseInterface):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None
        self.log.debug("Done")

    def _build(self):
        '''
            Build the interface. Should be called only once.
        '''
        self.log.debug("Building...")
        self.builder = Gtk.Builder()
        ui_file = os.path.join(GLADE_FOLDER, 'Browser.glade')
        self.builder.add_from_file(ui_file)
        # Set the logo
        self._setLogo()
        # Register main window
        self.window = self.builder.get_object("Main")
        self.window.resize(1300, 800)
        app = self.ctrl.services.getApplication()
        app.add_window(self.window)
        # Update the UI
        self.metatag_selected = self._getDefaultMetatag()
        self.selected_tag_name = ''
        self.files_limit = FILES_LIMIT
        # Set menu
        self.files_view_menu = FilesViewMenu.new(self.openFolder, self.openTagger, self.removeFile)
        # Setup files view
        self.files_store = Gtk.ListStore(int, str, Pixbuf, str)
        files_view = self.builder.get_object('FilesView')
        files_view.set_text_column(1)
        files_view.set_pixbuf_column(2)
        files_view.set_model(self.files_store)
        # Register the create events
        self.ctrl.onUpdateTags(self.recreateTagsList)
        self.ctrl.onUpdateAvailableMetatags(self.updateMetatagSelector)
        # Register the update events
        self.ctrl.onUpdateAvailableTags(self.updateTagsList)
        self.ctrl.onUpdateFiles(self.updateFilesList)
        self.ctrl.onUpdateUsedTags(self.updateUsedTags)
        # Add a signal handler
        self.builder.connect_signals(self)
        self.log.debug("Done")

    def _setLogo(self):
        '''
            Set the logo.
        '''
        logo = self.builder.get_object("Logo")
        logo_file = os.path.join(ConfigManager.getOverridesFolder(), "logo.png")
        if not os.path.exists(logo_file):
            logo_file = os.path.join(ICONS_FOLDER, "logo.png")
        logo.set_from_pixbuf(Pixbuf.new_from_file(logo_file))

    def show(self):
        '''
            Show the main window.
        '''
        if self.window is None:
            self._build()
        self.window.show()

    def recreateTagsList(self):
        self.tags_buttons = {}
        tags_list = self.builder.get_object("TagsList")
        # Clean the container
        self.cleanContainer(tags_list)
        # Add the tag buttons
        for tag in self.ctrl.tags:
            btn = self._createTagButton(tag, self.onTagSelected)
            tags_list.add(btn)
            self.tags_buttons[tag.id] = btn

    @inhibitSignals
    def updateMetatagSelector(self):
        '''
            Update the metatag selector.
        '''
        selector = self.builder.get_object("MetatagSelector")
        if len(self.ctrl.available_metatags) == 0:
            # TODO: better
            selector.hide()
            return
        if self.metatag_selected is None or not self._isCurrentMetatagAvailable():
            self.metatag_selected = self.ctrl.available_metatags[0]
        # Update the selector
        selector.remove_all()
        active_index = -1
        for index, metatag in enumerate(self.ctrl.available_metatags):
            selector.append_text(metatag.name)
            if metatag.name == self.metatag_selected.name:
                active_index = index
        # Set the active metatag
        if active_index > -1:
            selector.set_active(active_index)
        selector.show_all()

    def updateTagsList(self):
        '''
            Update the tags list.
        '''
        no_tags_label = self.builder.get_object("NoTagsAvailable")
        # Show/hide the no tags available label
        if len(self.ctrl.available_tags) == 0:
            no_tags_label.show()
        else:
            no_tags_label.hide()
        # Hide all the tags
        tags_list = self.builder.get_object("TagsList")
        for child in tags_list.get_children():
            child.hide()
        # Show available tags
        for tag in self.ctrl.available_tags:
            self.tags_buttons[tag.id].show()
        # Filter
        self.filterTagsList()

    def updateFilesList(self, append=False):
        if not append:
            self.files_store.clear()
        max_files = len(self.ctrl.files)
        max_index = min(len(self.files_store) + self.files_limit, max_files)
        for i in range(len(self.files_store), max_index):
            file = self.ctrl.files[i]
            pixbuf = self._getFilePixbuf(file)
            name = os.path.basename(file.name)
            self.files_store.append([file.id, name, pixbuf, file.name])
        files_view = self.builder.get_object('FilesView')
        files_view.show_all()
        # Show/hide the load more files button
        btn = self.builder.get_object("LoadMoreFiles")
        if len(self.files_store) == max_files:
            btn.hide()
        else:
            btn.show()

    def updateUsedTags(self):
        '''
            Update the list of the used tags.
        '''
        tags_list = self.builder.get_object("UsedTagsList")
        self.cleanContainer(tags_list)
        for tag in self.ctrl.used_tags:
            btn = self._createTagButton(tag, self.onTagRemoved)
            tags_list.add(btn)
        tags_list.show_all()

    def filterTagsList(self):
        '''
            Hide the tags with metatag not selected or name filtered.
        '''
        for tag in self.ctrl.available_tags:
            btn = self.tags_buttons[tag.id]
            if tag.metatag.id == self.metatag_selected.id and \
               self.selected_tag_name in tag.name.lower():
                btn.show()
            else:
                btn.hide()

    def _createTagButton(self, tag, activate_function=None):
        '''
            Create the select tag button.
        '''
        btn = Gtk.LinkButton()
        btn.set_label(tag.name)
        btn.set_size_request(160, 0)
        lbl = btn.get_children()[0]
        lbl.set_line_wrap(True)
        lbl.set_justify(Gtk.Justification.CENTER)
        if activate_function is not None:
            btn.connect("activate-link", activate_function, tag)
        return btn

    def _getFilePixbuf(self, file):
        '''
            Get the pixbuf for a file. Try to use the thumbnail if possible,
            fallback to the mime icon.

            :param dao.entities.Common.IFile file: File
            :return: Pixbuf for the file
            :rtype: GdkPixbuf.Pixbuf
        '''
        icon_name = "thumbnails/%d/%d.png" % (ICON_SIZE, file.id)
        icon_path = os.path.join(ConfigManager.profile_folder, icon_name)
        pixbuf = None
        # Try to load the thumbnail
        if os.path.exists(icon_path):
            try:
                pixbuf = Pixbuf.new_from_file(icon_path)
            except Exception:
                pixbuf = None
        # Use the mime icon
        if pixbuf is None:
            pixbuf = self._getMimePixbuf(file.mime)
        return pixbuf

    def _getMimePixbuf(self, mime):
        '''
            Get the icon pixbuf representing a mime.

            :param str mime: Mime
            :return: Pixbuf for the mime
            :rtype: GdkPixbuf.Pixbuf
        '''
        # Get the icon name
        theme = Gtk.IconTheme.get_default()
        name = None
        for icon_name in self._generateGtkIconNames(mime):
            if theme.has_icon(icon_name):
                name = icon_name
                break
        # Load the pixbuf
        try:
            pixbuf = theme.load_icon(name, ICON_SIZE, 0)
        except Exception:
            pixbuf = None
        return pixbuf

    def _generateGtkIconNames(self, mime):
        '''
            Generate a list of possible icon names
            for a given mimetype.

            :param str mime: Mime
            :return: Generator of possible icon names
            :rtype: Generator of str
        '''
        # Specific mime
        yield mime
        alt_mime = mime.replace('/','-')
        yield alt_mime
        yield 'gnome-mime-' + alt_mime
        # Generic mime
        gmime = mime.split('/')[0]
        yield gmime
        yield 'gnome-mime-' + gmime
        yield Gtk.STOCK_FILE

    def _isCurrentMetatagAvailable(self):
        '''
            Check if the current metatag is available.
        '''
        if self.metatag_selected is None:
            return False
        available = False
        for metatag in self.ctrl.available_metatags:
            if metatag.id == self.metatag_selected.id:
                available = True
                break
        return available

    def _getDefaultMetatag(self):
        name = ConfigManager.UI.getMetatagName()
        if name is None:
            return None
        default = None
        for metatag in self.ctrl.available_metatags:
            if metatag.name == name:
                default = metatag
                break
        return default

    def _getFileInStore(self, file_id):
        file = None
        for cfile in self.ctrl.files:
            if cfile.id == file_id:
                file = cfile
                break
        return file

    # Menu options
    def _getFilesViewSelected(self):
        '''
            Get the file currently selected in the files view.
            Return only if there is only one file selected.

            :return: The selected file if any, None otherwise
            :rtype: dao.entities.IFileLazy
        '''
        filesview = self.builder.get_object('FilesView')
        paths = filesview.get_selected_items()
        if len(paths) != 1:
            return None
        path = paths[0]
        file_id = self.files_store[path][0]
        file = self._getFileInStore(file_id)
        return file

    def openFolder(self, widget, data):
        file = self._getFilesViewSelected()
        if file is None:
            return
        folder = os.path.dirname(file.name)
        self.log.info("Opening folder: %s" % folder)
        openFile(folder)

    def openTagger(self, widget, data):
        file = self._getFilesViewSelected()
        if file is None:
            return
        self.log.info("Opening tagger for: %s" % file.name)
        self.ctrl.openTagger(file)

    def removeFile(self, widget, data):
        file = self._getFilesViewSelected()
        if file is None:
            return
        self.log.info("Confirm file removal: %s" % file.name)
        onConfirm = lambda : self.onRemoveFile(file)
        dialog = self.createConfirmationDialog("Confirm deletion",
                                               "Do you want to delete %s ?" % file.name,
                                               onConfirm)

    def onRemoveFile(self, file):
        self.log.info("Delete file: %s" % file.name)
        self.ctrl.removeFile(file)


    @withInhibit
    def onMetatagChange(self, widget):
        '''
            On metagag changed event.
        '''
        index = widget.get_active()
        self.metatag_selected = self.ctrl.available_metatags[index]
        self.filterTagsList()

    def onTagSelected(self, widget, tag):
        self.ctrl.addTag(tag)
        return True

    def onTagRemoved(self, widget, tag):
        self.ctrl.removeTag(tag)
        return True

    def onFilterByFileName(self, *args, **kwargs):
        # TODO
        pass

    def onFilterByTagName(self, widget):
        self.selected_tag_name = widget.get_text().lower()
        self.filterTagsList()

    def onLoadMoreFiles(self, *args, **kwargs):
        self.files_limit += FILES_LIMIT
        self.updateFilesList(append=True)

    def onFileClick(self, icon, treepath):
        findex = int(treepath.to_string())
        relpath = self.files_store[findex][-1]
        self.log.info("Opening file: %s" % relpath)
        openFile(relpath)

    def onButtonPress(self, widget, event):
        # event.button == 3 iff right-click
        if event.type != Gdk.EventType.BUTTON_PRESS or event.button != 3:
            return False
        coords = event.get_coords()
        ipath = widget.get_path_at_pos(coords[0], coords[1])
        if ipath is None:
            return False
        # Unselect other paths
        widget.unselect_all()
        # select the element
        widget.select_path(ipath)
        # Show right-click menu
        self.files_view_menu.popup(None, None, None, None, event.button, event.time)
        return True

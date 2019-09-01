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

SELECTOR_AUTOCOMPLETE = "Autocomplete"
SELECTOR_COMBOBOX = "ComboBox"

SELECTOR_FREETEXT = "FreeText"

DEFAULT_TARGET_NAME = "name"
DEFAULT_METATAGS = "metatags"

DEFAULT_WINDOW_SIZE = (600, 100)

class MoverUI(BaseInterface):

    log = createLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None
        self.metatag_selectors = {}
        self.custom_selectors = {}
        self.suggested_tags = []
        self.log.debug("Done")

    def _build(self):
        '''
            Build the interface.
        '''
        self.builder = Gtk.Builder()
        ui_file = os.path.join(GLADE_FOLDER, 'AddFile.glade')
        self.builder.add_from_file(ui_file)
        self.window = self.builder.get_object('Main')
        self.window.resize(*DEFAULT_WINDOW_SIZE)
        self.window.set_title("Move file to profile: %s" % ConfigManager.getProfileName())
        # Register window
        app = self.ctrl.services.getApplication()
        self.window.set_icon_from_file(app.icon_path)
        app.add_window(self.window)
        # Build custom components
        self._buildCustom()
        # Setup target name cell
        if self.ctrl.target_name_pattern is not None:
            entry = self.builder.get_object('DestinationName')
            entry.set_editable(False)
        # Register the update events
        self.ctrl.onUpdatePath(self.onPathChange)
        # Connect signals
        self.builder.connect_signals(self)

    def _buildCustom(self):
        '''
            Build custom components.
        '''
        custom_box = self.builder.get_object("CustomSelectors")
        # Build metatags selectors
        for metatag, selector_name in self.ctrl.metatags.items():
            selector = None
            if selector_name == SELECTOR_AUTOCOMPLETE:
                selector = self._buildAutocompletion(metatag)
            elif selector_name == SELECTOR_COMBOBOX:
                selector = self._buildComboBox(metatag)
            self.metatag_selectors[metatag] = selector
            # Add to UI
            self._addToCustomSelectors(custom_box, metatag, selector)
            '''
            box = self._buildSelectorBox(metatag, selector)
            custom_box.add(box)
            '''
        for entry_name, entry in self.ctrl.custom_entries.items():
            selector = None
            if entry["type"] == SELECTOR_FREETEXT:
                selector = self._buildFreeTextEntry(entry_name, entry)
            if selector is None:
                continue
            self.custom_selectors[entry_name] = selector
            self._addEntryToCustomSelectors(custom_box, entry_name, selector)
        custom_box.show_all()
        self.onSelectorValueChaged()
        # Build suggested tags
        pass

    def show(self):
        if self.window is None:
            self._build()
        self.window.show()

    def _addToCustomSelectors(self, custom_grid, metatag, selector):
        self._addEntryToCustomSelectors(custom_grid, metatag.name, selector)

    def _addEntryToCustomSelectors(self, custom_grid, entry_name, selector):
        label = Gtk.Label(entry_name + ": ")
        custom_grid.add(label)
        custom_grid.attach_next_to(selector, label, Gtk.PositionType.RIGHT, 1, 1)

    def _buildAutocompletion(self, metatag):
        '''
            Build an autocompletion box for a metatag.

            :param dao.entities.IMetatag: metatag
            :return: Autocompletion box for the metatag
            :rtype: Gtk.SearchEntry
        '''
        completion = Gtk.EntryCompletion.new()
        # Set model
        model = Gtk.ListStore(str)
        for tag in metatag.tags:
            model.append([tag.name])
        completion.set_model(model)
        completion.set_text_column(0)
        # Settings
        completion.set_inline_completion(False)
        completion.set_popup_completion(True)
        completion.set_popup_set_width(True)
        completion.set_popup_single_match(True)
        completion.set_inline_selection(True)
        # Create entry with completion
        entry = Gtk.SearchEntry()
        entry.set_completion(completion)
        # Set default value
        value = self._getMetatagDefaultValue(metatag)
        if value is not None:
            entry.set_text(value)
        # Connect events
        entry.connect("changed", self.onSelectorChanged, metatag)
        return entry

    def _buildComboBox(self, metatag):
        '''
            Build a selector box for a metatag.

            :param dao.entities.IMetatag: metatag
            :return: Combo box for the metatag
            :rtype: Gtk.ComboBoxText
        '''
        # Build the selector
        selector = Gtk.ComboBoxText()
        for tag in metatag.tags:
            selector.append_text(tag.name)
        # Get default value
        value = self._getMetatagDefaultValue(metatag)
        if value is None:
            selector.set_active(0)
        else:
            for i, tag in enumerate(metatag.tags):
                if tag.name == value:
                    selector.set_active(i)
                    break
        # Connect signals
        selector.connect("changed", self.onSelectorChanged, metatag)
        return selector

    def _buildFreeTextEntry(self, name, entry):
        default_value = entry["default-value"]
        selector = Gtk.Entry()
        selector.set_text(default_value)
        selector.connect("changed", self.onCustomSelectorChanged, name)
        return selector

    def _getMetatagDefaultValue(self, metatag):
        '''
            Get the default value for a metatag.

            :param dao.entitis.IMetatag: metatag
            :returns: Default value
            :rtype: str
        '''
        value = None
        if self.ctrl.default_values is not None and \
           DEFAULT_METATAGS in self.ctrl.default_values and \
           metatag.name in self.ctrl.default_values[DEFAULT_METATAGS]:
           value = self.ctrl.default_values[DEFAULT_METATAGS][metatag.name]
        return value

    def _buildSuggestedTagList(self):
        '''
            Build the suggested tags list.
        '''
        pass

    def _getSelectorValue(self, metatag, widget):
        '''
            Get the value of a custom selector.

            :param Gtk.ComboBoxText or Gtk.Entry: Custom selector
            :param dao.entities.IMetatag: metatag associated to the seletor
            :return: Value of the selector
            :rtype: str
        '''
        if type(widget) == Gtk.ComboBoxText:
            active = widget.get_active()
            tag = metatag.tags[active]
            value = tag.name
        else:
            value = widget.get_text().strip()
        return value

    def _getPatternBasicReplace(self):
        '''
            Common keywords.

            {_FileExtension}: source filename extension, None if it is a folder
        '''
        replacements = {}
        _, ext = os.path.splitext(self.ctrl.path)
        replacements["{_FileExtension}"] = ext
        return replacements

    def _getPatternMetatagsReplace(self):
        '''
            Get a dictionary with the replacements.
            e.g. {'Content' : 'documents'}

            :return: Dictionary with replacements
            :rtype: dict str -> srt
        '''
        replacements = {}
        for metatag, selector in self.metatag_selectors.items():
            value = self._getSelectorValue(metatag, selector)
            replace_key = "{%s}" % metatag.name
            replacements[replace_key] = value
        return replacements

    def _getPatternCustomEntriesReplace(self):
        replacements = {}
        for entry_name, selector in self.custom_selectors.items():
            value = self._getSelectorValue(None, selector)
            replace_key = "{%s}" % entry_name
            replacements[replace_key] = value
        return replacements

    def _getPatternAdvancedReplace(self, replacements):
        '''
            Get a dictionary with advanced replacements.
            These keys can be configured in the config folder/modules/moverKeys.py
            class.

            :param dict replacements: Metatag replacements are returned by _getPatternMetatagsReplace
            :return: Custom replacements
            :rtype: dict str -> str
        '''
        if self.ctrl.custom_target_keys is None or \
           self.ctrl.custom_target_keys_evaluator is None:
            return {}
        advanced = {}
        target_name = self.getDestinationName()
        self.log.info("Target name: %s" % target_name)
        for key in self.ctrl.custom_target_keys:
            replace_key = '{' + key + '}'
            value = self.ctrl.custom_target_keys_evaluator(key, self.ctrl.path, target_name, replacements)
            advanced[replace_key] = value
        return advanced

    def _evaluateTargetFolderPattern(self):
        '''
            Evaluate the target folder pattern using
            the values in the custom selectors.

            :return: Evaluated target folder
            :rtype: str
        '''
        target_folder = self._evaluatePattern(self.ctrl.target_folder_pattern)
        if target_folder.startswith('/'):
            target_folder = target_folder[1:]
        if not target_folder.endswith('/'):
            target_folder = target_folder + '/'
        return target_folder

    def _evaluateTargetNamePattern(self):
        return self._evaluatePattern(self.ctrl.target_name_pattern)

    def _evaluatePattern(self, pattern):
        if pattern is None:
            return '/'
        replacements = self._getPatternBasicReplace()
        replacements.update(self._getPatternMetatagsReplace())
        replacements.update(self._getPatternCustomEntriesReplace())
        advanced_replacements = self._getPatternAdvancedReplace(replacements)
        self.log.debug("Advanced replacements %s" % str(advanced_replacements))
        for key, value in replacements.items():
            pattern = pattern.replace(key, value)
        for key, value in advanced_replacements.items():
            pattern = pattern.replace(key, value)
        # Replace replicated /
        pattern = pattern.replace('//', '/')
        return pattern

    def _setDefaultTargetName(self, name):
        if self.ctrl.default_values is not None:
            if DEFAULT_TARGET_NAME in self.ctrl.default_values:
                name = self.ctrl.default_values[DEFAULT_TARGET_NAME]
        self.setDestinationName(name)
        self.onTargetPathChanged()

    def _getFileTags(self):
        '''
            Get the tags to be applied to the file.

            :return: list of tuples (tag_name, metatag)
            :rtype: list of (str, dao.entities.Common.IMetatag)
        '''
        tags = []
        for metatag, selector in self.metatag_selectors.items():
            name = self._getSelectorValue(metatag, selector)
            if len(name) > 0:
                tags.append((name, metatag))
        # TODO: Get suggested tags values
        return tags

    def _setAddEnabled(self, enable):
        self.log.debug("Enable button: %r" % enable)
        btn = self.builder.get_object('AddFileButton')
        btn.set_sensitive(enable)

    # Error message
    def _showErrorMessage(self, msg):
        label = self.builder.get_object('ErrorMessage')
        label.set_text(msg)

    def _hideErrorMessage(self):
        label = self.builder.get_object('ErrorMessage')
        label.set_text('')

    # Custom signals
    def onSelectorChanged(self, widget, metatag):
        self.log.debug("Selector for %s changed" % metatag.name)
        value = self._getSelectorValue(metatag, widget)
        self.log.debug("New value: %s" % value)
        self.onSelectorValueChaged()

    def onCustomSelectorChanged(self, widget, name):
        self.log.debug("Selector for %s changed" % name)
        self.onSelectorValueChaged()

    def onSelectorValueChaged(self):
        target_folder = self._evaluateTargetFolderPattern()
        self.setDestinationFolder(target_folder)
        if self.ctrl.target_name_pattern is not None:
            target_name = self._evaluateTargetNamePattern()
            self.setDestinationName(target_name)

    # Public methods
    def onPathChange(self):
        # Set basename
        basename = os.path.basename(self.ctrl.path)
        label = self.builder.get_object('SourceName')
        label.set_text('Source: %s' % basename)
        # Set default target name
        self._setDefaultTargetName(basename)
        # Re evaluate pattern
        self.onSelectorValueChaged()

    def setDestinationFolder(self, folder):
        self.log.debug("Set destination folder: %s" % folder)
        label = self.builder.get_object('DestinationLabel')
        label.set_text(folder)

    def getDestinationFolder(self):
        label = self.builder.get_object('DestinationLabel')
        return label.get_text()

    def getDestinationName(self):
        entry = self.builder.get_object('DestinationName')
        return entry.get_text()

    def setDestinationName(self, name):
        entry = self.builder.get_object('DestinationName')
        entry.set_text(name)

    # SIGNALS
    def onAdd(self, widget):
        tags = self._getFileTags()
        folder = self.getDestinationFolder()
        name = self.getDestinationName()
        target = self.ctrl.moveFileTo(folder, name)
        self.ctrl.addFile(target, tags)
        self.ctrl.stop()

    def onCancel(self, widget):
        self.ctrl.stop()

    def onUpdateFilename(self, widget):
        self.onSelectorValueChaged()
        self.onTargetPathChanged()

    def onTargetPathChanged(self):
        folder = self.getDestinationFolder()
        name = self.getDestinationName()
        path = self.ctrl.getTargetFullPath(folder, name)
        self.log.debug("New path: %s" % path)
        if not os.path.exists(path):
            self._setAddEnabled(True)
            self._hideErrorMessage()
        else:
            self._setAddEnabled(False)
            self._showErrorMessage("Target path already exists")

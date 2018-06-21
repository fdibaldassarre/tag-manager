#!/usr/bin/env python3

from gi.repository import Gtk

class BaseInterface:

    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.window = None
        self._inhibit_signals = False

    def show(self):
        raise NotImplementedError

    def close(self):
        if self.window is not None:
            self.window.close()

    def cleanContainer(self, container):
        children = container.get_children()
        for child in children:
            child.destroy()

    def createConfirmationDialog(self, title, question, callback_success=None, callback_failure=None):
        # create dialog
        dialog = Gtk.Dialog(title, self.window, 0,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_size(300, 100)
        label = Gtk.Label(question)
        box = dialog.get_content_area()
        box.add(label)
        # show and run
        dialog.show_all()
        response = dialog.run()
        # check response
        if response == Gtk.ResponseType.OK:
          if callback_success is not None:
            callback_success()
        else:
          if callback_failure is not None:
            callback_failure()
        # destory dialog
        dialog.destroy()
        return True

    def createMessageDialog(self, title, message):
        # create dialog
        dialog = Gtk.Dialog(title, self.window, 0,
                (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_size(300, 100)
        label = Gtk.Label(message)
        box = dialog.get_content_area()
        box.add(label)
        # show and run
        dialog.show_all()
        response = dialog.run()
        # destory dialog
        dialog.destroy()
        return True

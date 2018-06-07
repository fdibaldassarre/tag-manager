#!/usr/bin/env python3

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

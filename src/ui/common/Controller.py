#!/usr/bin/env python3

def ensureLoading(method):
    def newMethod(self, *args, **kwargs):
        if not self._loaded:
            self._loaded = True
            self.load()
        return method(self, *args, **kwargs)
    return newMethod

class BaseController:

    def __init__(self, services):
        self.services = services
        self.setupUpdateEvents()
        self.ui = None
        self._loaded = False

    def setupUpdateEvents(self):
        '''
            Initialize the lists of the functions
            to call on update event.
        '''
        self.on_update = {}

    def start(self):
        raise NotImplementedError

    def stop(self):
        pass

    def load(self):
        return NotImplementedError

    def onUpdate(self, event, func):
        self.on_update[event].append(func)
        func()

    def trigger(self, event, data=None):
        for f in self.on_update[event]:
            if data is None:
                f()
            else:
                f(*data)

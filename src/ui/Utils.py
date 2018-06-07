#!/usr/bin/env python3

def inhibitSignals(method):
    '''
        Do not trigger signals.
    '''
    def newMethod(self, *args, **kwargs):
        if self._inhibit_signals:
            res = method(self, *args, **kwargs)
        else:
            self._inhibit_signals = True
            res = method(self, *args, **kwargs)
            self._inhibit_signals = False
        return res
    return newMethod

def withInhibit(method):
    '''
        Force the method to respect the _inhibit_signals directive.
    '''
    def newMethod(self, *args, **kwargs):
        if self._inhibit_signals:
            return
        else:
            return method(self, *args, **kwargs)
    return newMethod

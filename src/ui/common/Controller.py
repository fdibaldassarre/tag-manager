#!/usr/bin/env python3

class BaseController:

    def __init__(self, services):
        self.services = services

    def start(self):
        raise NotImplemented

    def stop(self):
        pass

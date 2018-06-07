#!/usr/bin/env python3

class BaseError:
    def __init__(self, code, message):
        self.error = {
            "code": code,
            "message": message
        }

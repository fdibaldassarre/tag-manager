#!/usr/bin/env python3

class Named:

    def __init__(self, persistent_entity):
        self.id = persistent_entity.id
        self.name = persistent_entity.name

# File
class IFileLazy(Named):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)
        self.relpath = persistent_entity.relpath
        self.mime = persistent_entity.mime

class IFile(IFileLazy):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)
        self.tags = []
        for ptag in persistent_entity.tags:
            self.tags.append(ITagLazy(ptag))

# Tag
class ITagLazy(Named):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)
        self.metatag = IMetatagLazy(persistent_entity.metatag)
        '''
        self.metatag = None
        if persistent_entity.metatag is not None:
            self.metatag = IMetatagLazy(persistent_entity.metatag)
        '''

class ITag(ITagLazy):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)
        # self.files = persistent_entity.files
        self.files = []
        for pfile in persistent_entity.files:
            self.files.append(IFileLazy(pfile))

# Metatag
class IMetatagLazy(Named):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)

class IMetatag(IMetatagLazy):

    def __init__(self, persistent_entity):
        super().__init__(persistent_entity)
        self.tags = []
        for ptag in persistent_entity.tags:
            self.tags.append(Named(ptag))

# System File
class SystemFile():

    def __init__(self, src, name):
        self.src = src
        self.name = name

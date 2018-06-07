#!/usr/bin/env python3

from .Common import EntityDAO
from .Common import withSession

from .entities.Persistent import Metatag
from .entities.Common import IMetatag
from .entities.Common import IMetatagLazy

class MetatagsDAO(EntityDAO):

    _entity = IMetatag
    _entity_lazy = IMetatagLazy
    _persistent_entity = Metatag

    def insert(self, name=None):
        return super().insert(name=name)

metatagsDao = MetatagsDAO()

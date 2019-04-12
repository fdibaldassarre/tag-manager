#!/usr/bin/env python3

from flask import request

from src.dao import tagsDao
from src.web.Schemas import TagSchema
from src.web.Schemas import TagLazySchema

from .Common import BaseResource


class Tags(BaseResource):

    dao = tagsDao
    schema_single = TagSchema()
    schema_multi = TagLazySchema(many=True)
    schema_create = TagLazySchema()
    schema_update = TagLazySchema()
    create_required_params = ["name", "metatag"]

    def getEntities(self):
        '''
            Get all the resources.

            :return: List of resources
        '''
        related = request.args.getlist('related')
        name = request.args.get('name')
        if len(related) == 0 and not name:
            return self.dao.getAll()
        if not name:
            name_like = None
        else:
            name_like = "%" + name + "%"
        tag_codes = list(map(lambda c: int(c), related))
        return self.dao.getRelatedTags(tag_codes, name_like=name_like)

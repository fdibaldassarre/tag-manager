#!/usr/bin/env python3

from flask import request

from .Common import BaseResource

from src.dao import filesDao
from src.web.Schemas import FileSchema
from src.web.Schemas import FileLazySchema


class Files(BaseResource):

    dao = filesDao
    schema_single = FileSchema()
    schema_multi = FileLazySchema(many=True)
    schema_create = FileLazySchema()
    schema_update = FileLazySchema()
    create_required_params = ["name"]

    def getEntities(self):
        '''
            Get all the resources.

            :return: List of resources
        '''
        limit = request.args.get('limit')
        random = request.args.get('random')
        if random is not None:
            return self.dao.getRandom(limit)
        offset = request.args.get('offset')
        name = request.args.get('name')
        name_like = None
        if name is not None:
            name_like = '%' + name.replace(' ', '%') + '%'
        tags = request.args.getlist('tags')
        tag_codes = list(map(lambda c: int(c), tags))
        return self.dao.getByNameAndTags(name_like, tag_codes, offset=offset, limit=limit)

#!/usr/bin/env python3

from .Common import BaseResource


from src.dao import tagsDao
from src.web.Schemas import TagSchema
from src.web.Schemas import TagLazySchema


class Tags(BaseResource):

    dao = tagsDao
    schema_single = TagSchema()
    schema_multi = TagLazySchema(many=True)
    schema_create = TagLazySchema()
    schema_update = TagLazySchema()
    create_required_params = ["name", "metatag"]

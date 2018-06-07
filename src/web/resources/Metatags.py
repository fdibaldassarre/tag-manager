#!/usr/bin/env python3

from .Common import BaseResource


from src.dao import metatagsDao
from src.web.Schemas import MetatagSchema
from src.web.Schemas import MetatagLazySchema


class Metatags(BaseResource):

    dao = metatagsDao
    schema_single = MetatagSchema()
    schema_multi = MetatagLazySchema(many=True)
    schema_create = MetatagLazySchema()
    schema_update = MetatagLazySchema()
    create_required_params = ["name"]

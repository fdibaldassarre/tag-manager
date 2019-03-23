#!/usr/bin/env python3

from flask import request

from .Common import BaseResource

from src.dao import filesDao
from src.dao import tagsDao
from src.web.Schemas import TagLazySchema
from src.web.Schemas import FileSchema
from src.web.Errors import BaseError


class FileTags(BaseResource):

    tag_schema = TagLazySchema()
    file_schema = FileSchema()

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def put(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, fid):
        json_data = request.get_json()
        data, errors = self.tag_schema.load(json_data)
        if errors:
            error = BaseError(100, "Cannot load tag data")
            return self.marshal(error, self.schema_error), 400
        # Check minimum requirements
        if not "id" in data:
            error = BaseError(200, "Missing id in tag data")
            return self.marshal(error, self.schema_error), 400
        try:
            tag = tagsDao.getById(data["id"])
            file = filesDao.getById(fid)
            file = filesDao.addTag(file, tag)
        except Exception as e:
            error = BaseError(300, "Cannot add tag to file. Error: %s" % e)
            return self.marshal(error, self.schema_error), 400
        return self.marshal(file, self.file_schema), 201

    def delete(self, fid, tid):
        try:
            file = filesDao.getById(fid)
            tag = tagsDao.getById(tid)
            filesDao.removeTag(file, tag)
        except Exception as e:
            error = BaseError(300, "Cannot remove tag from file. Error: %s" % e)
            return self.marshal(error, self.schema_error), 400
        return None, 204

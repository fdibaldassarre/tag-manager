#!/usr/bin/env python3

from marshmallow import Schema
from marshmallow import fields

class NamedSchema(Schema):
    id = fields.Int()
    name = fields.Str()

# Lazy
class MetatagLazySchema(NamedSchema):
    pass

class TagLazySchema(NamedSchema):
    metatag = fields.Nested(MetatagLazySchema)

class FileLazySchema(NamedSchema):
    mime = fields.Str()

# Full schema
class MetatagSchema(MetatagLazySchema):
    tags = fields.List(fields.Nested(TagLazySchema))

class TagSchema(TagLazySchema):
    files = fields.List(fields.Nested(FileLazySchema))

class FileSchema(FileLazySchema):
    tags = fields.List(fields.Nested(TagLazySchema))

class BasicErrorSchema(Schema):
    code = fields.Int()
    message = fields.Str()

class ErrorSchema(Schema):
    error = fields.Nested(BasicErrorSchema)

class SystemFileSchema(Schema):
    name = fields.Str()
    src = fields.Str()

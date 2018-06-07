#!/usr/bin/env python3

from flask_restful import fields

episode_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "number": fields.String,
    "numberOrder":fields.Float,
    "status": fields.Integer,
    "link": fields.String,
    "filename": fields.String,
    "date": fields.String,
}

show_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "status": fields.Integer,
    "moduleName": fields.String,
    "moduleData": fields.String,
    "infoPage": fields.String,
    "totalEpisodes": fields.Integer,
    "producer": fields.String,
    "airDate": fields.String,
    "episodes": fields.List(fields.Nested(episode_fields)),
}

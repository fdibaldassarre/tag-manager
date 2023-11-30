#!/usr/bin/env python3

from flask import request
from flask_restful import Resource

from src.web.Schemas import ErrorSchema
from src.web.Errors import BaseError


class MarschalException(Exception):
    pass


class CommonResource(Resource):

    schema_error = ErrorSchema()

    def marshal(self, data, schema):
        '''
            Convert the given data to JSON with the given schema.

            :param data: Data
            :param schema: Schema
            :return: JSON serialized data
        '''
        return schema.dump(data)


class BaseResource(CommonResource):

    dao = None
    schema_single = None
    schema_multi = None
    schema_create = None
    schema_update = None
    create_required_params = []

    def get(self, eid=None):
        '''
            Execute a GET request with an optional parameter.

            :param int eid: Id of the resource
        '''
        if eid is None:
            entities = self.getEntities()
            return self.marshal(entities, self.schema_multi)
        else:
            entity = self.getEntity(eid)
            return self.marshal(entity, self.schema_single)

    def post(self):
        '''
            Execute a POST request.

            :param array data: request data
        '''
        # Get the request parameters
        json_data = request.get_json()
        data, errors = self.schema_create.load(json_data)
        if errors:
            error = BaseError(100, "Cannot load input data")
            return self.marshal(error, self.schema_error), 400
        # Check minimum requirements
        if not self.checkRequirementsCreate(data):
            error = BaseError(200, "Missing create requirements")
            return self.marshal(error, self.schema_error), 400
        # Create the entity
        entity = None
        try:
            entity = self.dao.insert(**data)
        except Exception as e:
            error = BaseError(300, "Cannot create the entity in database. Error: %s" % e)
            return self.marshal(error, self.schema_error), 400
        # Return the newly created entity
        return self.marshal(entity, self.schema_single), 201

    def put(self, eid):
        '''
            Execute a PUT request.

            :param int eid: Id of the resource
            :param array data: request data
        '''
        # Get the request parameters
        json_data = request.get_json()
        data, errors = self.schema_update.load(json_data)
        if errors:
            error = BaseError(100, "Cannot load input data")
            return self.marshal(error, self.schema_error), 400
        # Update the entity
        entity = None
        try:
            entity = self.dao.update(eid, **data)
        except Exception as e:
            error = BaseError(301, "Cannot update the entity in database. Error: %s" % e)
            return self.marshal(error, self.schema_error), 400
        # Return the newly updated entity
        return self.marshal(entity, self.schema_single)

    def delete(self, eid):
        '''
            Execute a DELETE request.

            :param int eid: Id of the resource
        '''
        success = self.deleteEntityPre(eid)
        if not success:
            return False
        try:
            self.dao.delete(eid)
        except Exception as e:
            error = BaseError(301, "Cannot delete the entity in database. Error: %s" % e)
            return self.marshal(error, self.schema_error), 400
        return None, 204

    def getEntity(self, eid):
        '''
            Get the resource with the given id.

            :param int eid: Id of the resource
            :return: Resource
        '''
        return self.dao.getById(eid)

    def getEntities(self):
        '''
            Get all the resources.

            :return: List of resources
        '''
        return self.dao.getAll()

    def updateEntity(self, entity, data):
        '''
            Update an entity with the given data.

            :return: The updated entity
        '''
        raise NotImplementedError()

    def deleteEntityPre(self, eid):
        '''
            Preliminary to delete an entity.

            :param int eid: Entity id
            :return: True on success, False otherwise
            :rtype: bool
        '''
        return True

    def deleteEntityPost(self):
        '''
            Cleanup after entity deletion.
        '''
        pass

    def checkRequirementsCreate(self, data):
        '''
            Check if all the required create parameters are present.

            :return: True if all paramters are present, false otherwise
            :rtype: bool
        '''
        valid = True
        for key in self.create_required_params:
            if key not in data or data[key] is None:
                valid = False
                break
        return valid

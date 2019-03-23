#!/usr/bin/env python3

import os

from src.Config import ConfigManager
from src.dao import filesDao
from src.dao.entities.Common import SystemFile
from src.web.Schemas import SystemFileSchema
from src.web.Errors import BaseError

from .Common import BaseResource


class FileList(BaseResource):

    file_schema = SystemFileSchema(many=True)

    def get(self, fid):
        '''
            Return the list of files in the given tagged folder.

            :params fid int: id of the file
            :return: list of files
            :rtype: list of SystemFile
        '''
        file = filesDao.getById(fid)
        if file is None:
            error = BaseError(100, "Missing file id")
            return self.marshal(error, self.schema_error), 400
        if file.mime != 'inode/directory':
            error = BaseError(100, "File is not a folder")
            return self.marshal(error, self.schema_error), 400
        file_list = self.getFilesContained(file.name)
        return self.marshal(file_list, self.file_schema)

    def getFilesContained(self, fname):
        file_list = []
        path = os.path.join(ConfigManager.getRoot(), fname)
        if not os.path.exists(path):
            return []
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    name = entry.name
                    relpath = os.path.join(fname, name)
                    sysfile = SystemFile(relpath, name)
                    file_list.append(sysfile)
        file_list.sort(key=lambda s: s.name)
        return file_list

    def put(self, fid):
        raise NotImplementedError()

    def post(self, fid):
        raise NotImplementedError()

    def delete(self, fid):
        raise NotImplementedError()

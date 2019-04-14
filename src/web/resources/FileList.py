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
        path = os.path.join(file.relpath, file.name)
        file_list = self.getFilesContained(path)
        return self.marshal(file_list, self.file_schema)

    def getFilesContained(self, fname):
        file_list = []
        path = os.path.join(ConfigManager.getRoot(), fname)
        if not os.path.exists(path):
            return []
        for root, dirs, files in os.walk(path):
            for name in files:
                fullpath = os.path.join(root, name)
                relpath = os.path.relpath(fullpath, start=ConfigManager.getRoot())
                rname = os.path.relpath(fullpath, start=path)
                sysfile = SystemFile(relpath, rname)
                file_list.append(sysfile)
        file_list.sort(key=lambda s: s.name)
        return file_list


    def put(self, fid):
        raise NotImplementedError()

    def post(self, fid):
        raise NotImplementedError()

    def delete(self, fid):
        raise NotImplementedError()

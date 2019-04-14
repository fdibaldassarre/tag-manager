#!/usr/bin/env python3

from sqlalchemy.orm import exc

from .Common import EntityDAO
from .Common import withSession
from .Common import returnNonPersistent
from .Common import returnNonPersistentFull

from .entities.Persistent import File
from .entities.Persistent import Tag
from .entities.Common import IFile
from .entities.Common import IFileLazy

class TagNotFound(Exception):
    pass

class FilesDAO(EntityDAO):

    _entity = IFile
    _entity_lazy = IFileLazy
    _persistent_entity = File

    def insert(self, name=None, relpath=None, mime=None):
        return super().insert(name=name, relpath=relpath, mime=mime)

    @withSession
    @returnNonPersistentFull
    def addTag(self, file, tag):
        '''
            Add a tag to a file.

            :param entities.Common.IFile: File
            :param entities.Common.ITag: Tag
            :return: The file with the given tag added
            :rtype: entities.Common.IFile
        '''
        ptag = self._session.query(Tag).filter_by(id=tag.id).one()
        pfile = self._getById(file.id)
        if not ptag in pfile.tags:
            pfile.tags.append(ptag)
        return pfile

    @withSession
    @returnNonPersistentFull
    def removeTag(self, file, tag):
        '''
            Remove a tag from a file.

            :param entities.Common.IFile: File
            :param entities.Common.ITag: Tag
            :return: The file without the given tag removed
            :rtype: entities.Common.IFile
        '''
        ptag = self._session.query(Tag).filter_by(id=tag.id).one()
        pfile = self._getById(file.id)
        if ptag in pfile.tags:
            pfile.tags.remove(ptag)
        return pfile

    @withSession
    @returnNonPersistent
    def getByNameAndTags(self, name=None, tags=None, offset=None, limit=None):
        '''
            Find all the files with a certain name and
            all the given tags.

            :param str name: Name of the file
            :param list tags: List of tags
            :return: All the files with given name and tags
            :rtype: list of entities.Common.IFile
        '''
        query = self._session.query(File)
        if name is not None:
            query = query.filter(File.name.like(name))
        if tags is not None:
            for tag in tags:
                ptag = Tag(id=self._getTagId(tag)) # self._session.query(Tag).filter_by(id=tag.id).one()
                query = query.filter(File.tags.contains(ptag))
        query = query.order_by(File.name)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def _getTagId(self, tag):
        tag_id = None
        if type(tag) == int:
            tag_id = tag
        else:
            tag_id = tag.id
        return tag_id

filesDao = FilesDAO()

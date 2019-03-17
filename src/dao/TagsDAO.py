#!/usr/bin/env python3

from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from .Common import EntityDAO
from .Common import withSession
from .Common import returnNonPersistent

from .entities.Persistent import File
from .entities.Persistent import Tag
from .entities.Persistent import file_tags
from .entities.Common import ITag
from .entities.Common import ITagLazy
from .entities.Common import IMetatag
from .entities.Common import IMetatagLazy


class TagsDAO(EntityDAO):

    _entity = ITag
    _entity_lazy = ITagLazy
    _persistent_entity = Tag
    _options = joinedload(Tag.metatag)

    def insert(self, name=None, metatag=None):
        values = {}
        values['name'] = name
        if metatag is not None:
            values['metatag_id'] = self._getMetatagId(metatag)
        return super().insert(**values)

    def update(self, tag, name=None, metatag=None):
        values = {}
        if name is not None:
            values['name'] = name
        if metatag is not None:
            values['metatag_id'] = self._getMetatagId(metatag)
        return super().update(tag, **values)

    def _getMetatagId(self, metatag):
        metatag_id = None
        if type(metatag) == int:
            metatag_id = metatag
        elif type(metatag) == IMetatag or type(metatag) == IMetatagLazy:
            metatag_id = metatag.id
        else:
            metatag_id = metatag["id"]
        return metatag_id

    @withSession
    @returnNonPersistent
    def getAllWithOneFileTagged(self):
        query = self._session.query(Tag).join(Tag.files).order_by(Tag.name)
        return query.all()

    @withSession
    @returnNonPersistent
    def getByNameLike(self, name):
        '''
            Find all the tags with a certain name.

            :param str name: Name of the tag
            :return: All the tags with given name
            :rtype: list of entities.Common.ITag
        '''
        query = self._session.query(Tag)
        if name is not None:
            query = query.filter(Tag.name.like(name))
        query = query.options(self._options)
        return query.all()

    @withSession
    @returnNonPersistent
    def getCommonTags(self, files):
        '''
            Find all the tags in common among the given files.

            @Deprecated

            :param files: List of IFile
            :return: List of tags
            :rtype: list of ITag
        '''
        files_codes = list(map(lambda f: f.id, files))
        # Get the files ids
        query = self._session.query(Tag).outerjoin(Tag.files).filter(File.id.in_(files_codes))
        query = query.options(self._options)
        return query.all()

    @withSession
    @returnNonPersistent
    def getRelatedTags(self, tags):
        '''
            Find all the tags related with any of the given tags.
            A tag is related to another if there is at least one file with
            both tags.

            :param tags: List of ITag
            :return: List of tags
            :rtype: list of ITag
        '''
        tag_codes = list(map(lambda t: t.id, tags))
        query = self._session.query(Tag).distinct()\
            .join(file_tags, Tag.id == file_tags.c.Tag)
        file_tag_aliases = {}
        for tag_code in tag_codes:
            alias = aliased(file_tags, name="TagFiles_%d" % tag_code)
            query = query.join(alias, file_tags.c.File == alias.c.File)
            file_tag_aliases[tag_code] = alias
        # Filter
        for tag_code, alias in file_tag_aliases.items():
            query = query.filter(alias.c.Tag == tag_code)
        query = query.options(self._options)
        return query.all()


tagsDao = TagsDAO()

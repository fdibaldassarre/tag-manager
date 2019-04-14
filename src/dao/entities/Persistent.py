#!/usr/bin/env python3

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Table

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

# Association tables
file_tags = Table('FileTags', Base.metadata,
                  Column('File', ForeignKey('Files.id'), primary_key=True),
                  Column('Tag', ForeignKey('Tags.id'), primary_key=True)
                 )

# Entities
class File(Base):
    __tablename__ = "Files"
    __table_args__ = (UniqueConstraint('relpath', 'name', name='_file_name_uc'),
                     )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    relpath = Column(String, nullable=False, index=True)
    mime = Column(String, nullable=False)

    tags = relationship('Tag',
                        secondary=file_tags,
                        back_populates='files')

class Tag(Base):
    __tablename__ = "Tags"
    __table_args__ = (UniqueConstraint('name', name='_tag_name_uc'),
                     )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    metatag_id = Column(Integer, ForeignKey('Metatags.id'), nullable=False, index=True)

    metatag = relationship('Metatag', back_populates='tags')

    files = relationship('File',
                         secondary=file_tags,
                         back_populates='tags')

class Metatag(Base):
    __tablename__ = "Metatags"
    __table_args__ = (UniqueConstraint('name', name='_metatag_name_uc'),
                     )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)

    tags = relationship('Tag',
                        order_by=Tag.name,
                        back_populates='metatag')

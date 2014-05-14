# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, BLOB
#from sqlalchemy.orm import relation, backref

from happy.model import DeclarativeBase, metadata, DBSession


class UserFile(DeclarativeBase):
    __tablename__ = 'userfile'
        
    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(255), nullable=False)
    filecontent = Column(BLOB)
    author = Column(Integer, ForeignKey('tg_user.user_id',onupdate="CASCADE", ondelete="CASCADE"))
    
    def __init__(self, filename, filecontent, author):
        self.filename = filename
        self.filecontent = filecontent
        self.author = author

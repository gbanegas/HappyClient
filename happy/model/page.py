from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer,  Text

from happy.model import User

from happy.model import DeclarativeBase, metadata, DBSession

import textile

class Page(DeclarativeBase):
	__tablename__ = 'page'

	id = Column(Integer, primary_key=True)
	pagename = Column(Text, unique=True)
	title = Column(Text, nullable=False)
	data = Column(Text, nullable=False)
	date = Column(Text,nullable=False)
	author = Column(Integer, ForeignKey('tg_user.user_id',onupdate="CASCADE", ondelete="CASCADE"))
	tags = Column(Text)

	def __init__(self, pagename, title, data, date, author, tags):
		self.pagename = pagename
		self.title = title
		self.data = data
		self.date = date
		self.author = author
		self.tags = tags



	def getAuthor(self):
		username = str(DBSession.query(User).filter_by(user_id=self.author).one().display_name)
		return username
	
	def getTags(self):
		self.tags = self.tags.replace(',', ' ');
		tagList = self.tags.split();
		return tagList;

	def getHtmlData(self):
		return textile.textile(self.data)





# -*- coding: utf-8 -*-
"""File Controller"""
import re
import time
import datetime

from pagecontroller import PageController
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from happy import model
from happy.controllers.secure import SecureController
from happy.model import DBSession, metadata
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from happy.lib.base import BaseController
from happy.controllers.error import ErrorController
from happy.model.page import Page
from happy.model.auth import User
from happy.model.userfile import UserFile
from docutils.core import publish_parts
import textile

forbidden_files = [".js", ".htm", ".html", ".mp3"]
class FileController(BaseController):

    def saveFile(self, userfile, author):
        for forbidden_file in forbidden_files:
            if userfile.filename.find(forbidden_file) != -1:
                return redirect("/")
        filecontent = userfile.file.read()
        author_id = DBSession.query(User).filter_by(user_name=author).first().user_id
        new_file = UserFile(filename=userfile.filename, filecontent=filecontent, author=author_id)
        DBSession.add(new_file)
        DBSession.flush()
        return new_file.id
   	
   	
   	

        @expose()
        def delete(self, fileid):
            try:
                userfile = DBSession.query(UserFile).filter_by(id=fileid).one()
            except:
                return redirect("/")
            DBSession.delete(userfile)
            return redirect("/")
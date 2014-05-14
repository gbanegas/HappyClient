# -*- coding: utf-8 -*-
"""Main Controller"""

import re
import time
import datetime

from pagecontroller import PageController
from filecontroller import FileController
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context,response
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
from happy.model.userfile import UserFile
from docutils.core import publish_parts
import textile

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

__all__ = ['RootController']
pageController = PageController();
fileController = FileController();


class RootController(BaseController):
    """
    The root controller for the happy application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "happy"

    @expose('happy.templates.index')
    def index(self):
        """Handle the front-page."""
        pages = pageController.getAllPages()
        return dict(page='index',pages=pages)


    @expose('happy.templates.page')
    def page(self,pagename):
        page = pageController.getPage(pagename)
        #content = publish_parts(page.data, writer_name="html")["html_body"]
        content = textile.textile( page.data)
        root = url('/')
        return dict(content=content, wikipage=page)

    @expose('happy.templates.result')
    def searchtag(self,tag):
        pages = pageController.searchPages(tag)
        return dict(page='result',pages=pages)

    @expose('happy.templates.fileupload')
    def view(self):
        current_files = DBSession.query(UserFile).all()
        return dict(current_files=current_files)


    @expose()
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def save_file(self, userfile):
        author =  request.identity['repoze.who.userid']
        file_id = fileController.saveFile(userfile,author)
        redirect("/viewfile/"+str(file_id))

    @expose()
    def viewfile(self, fileid):
            try:
                userfile = DBSession.query(UserFile).filter_by(id=fileid).one()
            except:
                redirect("/")
            content_types = {
                'display': {'.png': 'image/jpeg', '.jpeg':'image/jpeg', '.jpg':'image/jpeg', '.gif':'image/jpeg', '.txt': 'text/plain'},
                'download': {'.pdf':'application/pdf', '.zip':'application/zip', '.rar':'application/x-rar-compressed'}
            }
            for file_type in content_types['display']:
                if userfile.filename.endswith(file_type):
                    response.headers["Content-Type"] = content_types['display'][file_type]
            for file_type in content_types['download']:
                if userfile.filename.endswith(file_type):
                    response.headers["Content-Type"] = content_types['download'][file_type]
                    response.headers["Content-Disposition"] = 'attachment; filename="'+userfile.filename+'"'
            if userfile.filename.find(".") == -1:
                response.headers["Content-Type"] = "text/plain"
            return userfile.filecontent

    
    @expose(template="happy.templates.edit")
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def edit(self, pagename):
        page = pageController.getPage(pagename)
        return dict(wikipage=page)


    @expose("happy.templates.pagelist")
    def pagelist(self):
        pages = pageController.getAllNamePages()
        return dict(pages=pages)

    @expose("wiki20.templates.edit")
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def notfound(self, pagename):
        page = Page(pagename=pagename, data="")
        DBSession.add(page)
        return dict(wikipage=page)
    
    @expose(template="happy.templates.add")
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def add(self):
        page = Page()
        return dict(wikipage=page)

    @expose()
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def save_new(self, pagename, title, data, tags,submit):
        author =  request.identity['repoze.who.userid']
        pagename = title.replace(' ','')
        page = pageController.save(pagename, title, data, author, tags)
        DBSession.add(page)
        redirect("/page/" + pagename)


    @expose()
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def save(self, pagename, data, title, submit):
        page = DBSession.query(Page).filter_by(pagename=pagename).one()
        page.data = data
        page.title = title
        page.date = time.strftime("%c")
        redirect("/page/" + pagename)

    @expose('happy.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')


    @expose('happy.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(page='data', params=kw)
   
    @expose('happy.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('happy.templates.index')
    @require(predicates.is_user('manager', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('happy.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login', params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)

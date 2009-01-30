#!/usr/bin/python
# -*- coding: utf-8

import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from hivemind.hmdb import Planet
from hivemind.hmdb import Fleet
from hivemind.hivemind import Updater


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('index.html', {}))


application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

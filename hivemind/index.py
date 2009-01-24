    #!/usr/bin python
# -*- coding: utf-8 -*-

import os
import cgi
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


HAPI_BASE_URL = 'http://www.hyperiums.com/servlet/HAPI'
ALLOWED_USERS = ('sopo')


class HAPIlogin(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'hapilogin.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        login = cgi.escape(self.request.get('login')).lower()
        hapikey = cgi.escape(self.request.get('hapikey'))
        if login in ALLOWED_USERS:
            response = urlfetch.fetch(''.join([HAPI_BASE_URL,
                                               '?game=Hyperiums5',
                                               '&player=', login,
                                               '&hapikey=', hapikey]))
            if response.status_code == 200:
                hapi_req_url = '&'.join(response.content.split('&')[0:-1])
                print
                print hapi_req_url
            path = os.path.join(os.path.dirname(__file__), 'index.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'error.html')
        self.response.out.write(template.render(path, {}))


class Update(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'update.html')
        self.response.out.write(template.render(path, template_values))


class Search(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'search.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/hivemind', HAPIlogin),
                                      ('/hivemind/update', Update),
                                      ('/hivemind/search', Search)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

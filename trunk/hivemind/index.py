#!/usr/bin python
# -*- coding: utf-8 -*-

import os
import cgi
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from hivemind.hmdb import Planet
from hivemind.hmdb import Fleet
from hivemind.hivemind import Updater


class Const:
    HAPI_BASE_URL = 'http://www.hyperiums.com/servlet/HAPI'
    HAPI_REQ_URL = ''
    ALLOWED_USERS = ('sopo')


class HAPIlogin(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'hapilogin.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        login = cgi.escape(self.request.get('login')).lower()
        hapikey = cgi.escape(self.request.get('hapikey'))
        if login in Const.ALLOWED_USERS:
            response = urlfetch.fetch(''.join([Const.HAPI_BASE_URL,
                                               '?game=Hyperiums5',
                                               '&player=', login,
                                               '&hapikey=', hapikey]))
            if response.status_code == 200:
                Const.HAPI_REQ_URL = '?'.join([Const.HAPI_BASE_URL,
                                '&'.join(response.content.split('&')[0:-1])])
            path = os.path.join(os.path.dirname(__file__), 'index.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'error.html')
        self.response.out.write(template.render(path, {}))


class Update(webapp.RequestHandler):
    def post(self):
        response = urlfetch.fetch('&'.join([Const.HAPI_REQ_URL,
                                            'request=getfleetsinfo',
                                            'planet=*',
                                            'data=foreign_planets']))
        if response.status_code == 200:
            database = Updater(response.content)
            database.update()
            status = 'Database successfully updated'
        else:
            status = 'Error while updating database'
        template_values = {
            'status': status
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Search(webapp.RequestHandler):
    def post(self):
        searchby = self.request.get('searchby')
        searched_term = cgi.escape(self.request.get('searched_term')).lower()
        if searchby == 'player':
            query = Fleet.gql("WHERE owner_name = :1 "
                              "ORDER BY location_name",
                              searched_term)
        elif searchby == 'planet':
            query = Fleet.gql("WHERE location_name = :1 "
                              "ORDER BY owner_name",
                              searched_term)
        results = query.fetch(999)
        template_values = {
            'searched_term': searched_term,
            'searchby': searchby,
            'search_result': results
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/hivemind', HAPIlogin),
                                      ('/hivemind/update', Update),
                                      ('/hivemind/search', Search)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

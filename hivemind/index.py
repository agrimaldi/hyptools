#!/usr/bin python
# -*- coding: utf-8 -*-

import os
import cgi
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from hivemind.hmdb import Fleet
from hivemind.hivemind import Updater


HAPI_BASE_URL = 'http://www.hyperiums.com/servlet/HAPI'
ALLOWED_USERS = ("sopo", "zeddie", "jester.8", "keffer", "gerbo")


class HAPIlogin(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'hapilogin.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        login = cgi.escape(self.request.get('login')).lower()
        hapikey = cgi.escape(self.request.get('hapikey'))
        if login in ALLOWED_USERS:
            try:
                response = urlfetch.fetch(''.join([
                    HAPI_BASE_URL,
                    '?game=Hyperiums5',
                    '&player=', login,
                    '&hapikey=', hapikey
                ]))
                if response.status_code == 200:
                    memcache.set(
                        key="hapi_req_url",
                        value='?'.join([
                            HAPI_BASE_URL,
                            '&'.join(response.content.split('&')[0:-1])]),
                        time=900
                    )
                path = os.path.join(os.path.dirname(__file__), 'index.html')
            except DownloadError:
                path = os.path.join(os.path.dirname(__file__), 'auth_fail.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'access_denied.html')
        self.response.out.write(template.render(path, {}))


class Update(webapp.RequestHandler):
    def get(self):
        memcache.incr("chunk_counter")
        self.post()

    def post(self):
        chunk_counter = memcache.get("chunk_counter")
        if chunk_counter == 0:
            tmp_resp = urlfetch.fetch('&'.join([
                memcache.get("hapi_req_url"),
                'request=getfleetsinfo',
                'planet=*',
                'data=foreign_planets']))
            memcache.add(
                key="response",
                value=tmp_resp,
                time=60
            )
        response = memcache.get("response")
        if response.status_code == 200:
            if chunk_counter == 0:
                database = Updater(response.content)
                database.chop(chunk_size=800)
                memcache.set(
                    key="database",
                    value=database,
                    time=60
                )
            database = memcache.get("database")
            database.update(database.chunk_list[chunk_counter])
            memcache.set(
                key="database",
                value=database,
                time=60
            )
            if chunk_counter < len(database.chunk_list)-1:
                self.redirect("/hivemind/update")
            else:
                memcache.delete(key="chunk_counter")
            update_status = 'Database successfully updated'
        else:
            update_status = 'Error while updating database'
        template_values = {
            'update_status': update_status
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Search(webapp.RequestHandler):
    def post(self):
        searchby = self.request.get('searchby')
        searched_term = cgi.escape(self.request.get('searched_term')).lower()
        res_fleets = []
        res_players = []
        res_planets = []

        if searchby == 'player':
            query = Fleet.gql(
                "WHERE owner_name = :1 "
                "ORDER BY location_name",
                searched_term
            )
            for result in query:
                if result.location not in res_planets:
                    res_planets.append(result.location)
                    print res_planets
                    print result
                    print result.location.name
                    print
#                res_fleets.append(result)
            template_values = {
                'searchby': searchby,
                'res_planets': res_planets
            }

        elif searchby == 'planet':
            query = Fleet.gql(
                "WHERE location_name = :1 "
                "ORDER BY owner_name",
                searched_term
            )
            for result in query:
                res_fleets.append(result)
            if res_fleets:
                template_values = {
                    'searchby': searchby,
                    'location': res_fleets[0].location,
                    'res_fleets': res_fleets
                }
            else:
                template_values = {
                    'search_status': "Planet not found"
                }
#        template_values = {
##            'searched_term': searched_term,
#            'searchby': searchby,
#            'res_location': res_location,
#            'results': res_fleets
#        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([
    ('/hivemind', HAPIlogin),
    ('/hivemind/update', Update),
    ('/hivemind/search', Search)],
    debug=True)

def main():
    memcache.add(key="chunk_counter", value=0, time=60)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

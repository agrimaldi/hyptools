#!/usr/bin python
# -*- coding: utf-8 -*-

import os
import cgi
#import urllib2
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from hivemind.hmdb import Fleet
from hivemind.hivemind import Updater


HAPI_BASE_URL = 'http://www.hyperiums.com/servlet/HAPI'
ALLOWED_USERS = ("sopo",
                 "zeddie",
                 "jester.8",
                 "keffer",
                 "gerbo",
                 "slyons93",
                 "om49",
                 "hactar")


class HAPIlogin(webapp.RequestHandler):
    """HAPI login handler
    """
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'hapilogin.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        login = cgi.escape(self.request.get('login')).lower()
        hapikey = cgi.escape(self.request.get('hapikey'))
        if login in ALLOWED_USERS:
            try:
                response = urlfetch.fetch(''.join([HAPI_BASE_URL,
                                                   '?game=Hyperiums5',
                                                   '&player=', login,
                                                   '&hapikey=', hapikey]))
                if response.status_code == 200:
                    memcache.set(
                        key="hapi_req_url",
                        value='?'.join([
                            HAPI_BASE_URL,
                            '&'.join(response.content.split('&')[0:-1])]),
                        time=900
                    )
                path = os.path.join(os.path.dirname(__file__), 'index.html')
            except urlfetch.DownloadError:
                path = os.path.join(os.path.dirname(__file__), 'auth_fail.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'access_denied.html')
        self.response.out.write(template.render(path, {}))


class HAPIlogout(webapp.RequestHandler):
    """HAPI logout handler
    """
    def post(self):
        response = urlfetch.fetch('&'.join([memcache.get("hapi_req_url"),
                                            'request=logout']))
        if response.status_code == 200 and response.content == 'status=ok':
            self.redirect('/hivemind')


class Update(webapp.RequestHandler):
    """Update handler
    """
    def get(self):
        """Only purpose of this method is to call the <post> method in case
        of a redirection
        """
        memcache.incr("chunk_counter")
        self.post()

    def post(self):
        chunk_counter = memcache.get("chunk_counter")

        # Fetch data only the first time
        if chunk_counter == 0:
            tmp_resp = urlfetch.fetch('&'.join([memcache.get("hapi_req_url"),
                                                'request=getfleetsinfo',
                                                'planet=*',
                                                'data=foreign_planets']))
            memcache.add("response", tmp_resp, 120)

        response = memcache.get("response")
        if response.status_code == 200:

            # If first iteration, create an Updater object and chop the data
            if chunk_counter == 0:
                database = Updater(response.content)
                database.chop(1500)
                memcache.set("database", database, 120)

            # Update the database with the current chunk
            database = memcache.get("database")
            database.update(database.chunk_list[chunk_counter])
            memcache.set("database", database, 120)

            if chunk_counter < len(database.chunk_list)-1:
                self.redirect("/hivemind/update")
            else:
                memcache.delete(key="chunk_counter")
            update_status = 'Database successfully updated'
        else:
            update_status = 'Error while updating database'

        template_values = {'update_status': update_status}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Search(webapp.RequestHandler):
    """Search handler
    Handles searching by planet name or by player name through a POST method.
    """
    def post(self):
        searchby = self.request.get('searchby')
        searched_term = cgi.escape(self.request.get('searched_term')).lower().strip()
        res_fleets = []
        res_planets = []

        # Search by player
        if searchby == 'player':
            tmp_fleet = []
            tmp_planet = ''
            query = Fleet.gql("WHERE owner_name = :1 "
                              "ORDER BY location_name",
                              searched_term)
            if query.get():
                for fleet in query:
                    if fleet.location_name == tmp_planet or tmp_planet == '':
                        tmp_fleet.append(fleet)
                    else:
                        res_planets.append(tmp_fleet)
                        tmp_fleet = []
                        tmp_fleet.append(fleet)
                    tmp_planet = fleet.location_name
                res_planets.append(tmp_fleet)
                template_values = {
                    'searchby': searchby,
                    'player': res_planets[0][0].owner.name,
                    'res_planets': res_planets
                }
            else:
                template_values = {'search_status': "<p>Player not found</p>"}

        # Search by planet
        elif searchby == 'planet':
            query = Fleet.gql("WHERE location_name = :1 "
                              "ORDER BY owner_name",
                              searched_term)
            if query.get():
                for fleet in query:
                    res_fleets.append(fleet)
                template_values = {
                    'searchby': searchby,
                    'location': res_fleets[0].location,
                    'res_fleets': res_fleets
                }
            else:
                template_values = {'search_status': "<p>Planet not found</p>"}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/hivemind', HAPIlogin),
                                      ('/hivemind/logout', HAPIlogout),
                                      ('/hivemind/update', Update),
                                      ('/hivemind/search', Search)],
                                     debug=True)

def main():
    memcache.add(key="chunk_counter", value=0, time=120)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

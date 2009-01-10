#!/usr/bin python
# -*- coding:utf-8

import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from battle_reports.battlereports import Analysis


class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class BattleReport(webapp.RequestHandler):
    def post(self):
        raw_report = cgi.escape(self.request.get('content'))
        nice_report = Analysis(raw_report).getNiceReports()
        template_values = {
            'nice_report': nice_report,
        }
        path = os.path.join(os.path.dirname(__file__), 'result.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/battle_reports', MainPage),
                                      ('/battle_reports/', MainPage),
                                      ('/battle_reports/result', BattleReport),
                                      ('/battle_reports/result/', BattleReport)
                                      ],
                                     debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

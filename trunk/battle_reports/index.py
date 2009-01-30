#!/usr/bin python
# -*- coding:utf-8

import os
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from battle_reports.battlereports import Analysis


class SubmitReport(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        raw_report = cgi.escape(self.request.get('content'))
        nice_reports = Analysis(raw_report)
        template_values = {
            "planet_names":            nice_reports.keys(),
            "battle_report_objects":   nice_reports.values()
        }
        path = os.path.join(os.path.dirname(__file__), 'result.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/battle_reports', SubmitReport),
                                      ('/battle_reports/', SubmitReport)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

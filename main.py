#!/usr/bin/env python

import base64
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import fetch

_base_js_escapes = (
  ('\\', r'\u005C'),
  ('\'', r'\u0027'),
  ('"', r'\u0022'),
  ('>', r'\u003E'),
  ('<', r'\u003C'),
  ('&', r'\u0026'),
  ('=', r'\u003D'),
  ('-', r'\u002D'),
  (';', r'\u003B'),
  (u'\u2028', r'\u2028'),
  (u'\u2029', r'\u2029'),
)
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))

def escapejs(value):
  """Hex encodes characters for use in JavaScript strings."""
  for bad, good in _js_escapes:
    value = value.replace(bad, good)
  return value

class EchoHandler(webapp.RequestHandler):
  """Echoes an uploaded file via JSONP."""
  def get(self):
    url = self.request.GET.get('url', None)
    if url is None:
      self.error(404)
      return
    callback = self.request.GET.get('callback', '')
    headers = {}
    if 'Cache-Control' in self.request.headers:
      headers['Cache-Control'] = self.request.headers.get('Cache-Control')
    raw = fetch(url, headers=headers)
    self.response.headers["Content-Type"] = "text/javascript"
    self.response.out.write('%s("' % callback)
    self.response.out.write('data:%s;base64,' % escapejs(raw.headers.get('Content-Type', '')))
    self.response.out.write(base64.b64encode(raw.content))
    self.response.out.write('")')

class ProxyHandler(webapp.RequestHandler):
  """Proxies a URL via JSONP."""
  def get(self):
    url = self.request.GET.get('url', None)
    if url is None:
      self.error(404)
      return
    callback = self.request.GET.get('callback', '')
    headers = {}
    if 'Cache-Control' in self.request.headers:
      headers['Cache-Control'] = self.request.headers.get('Cache-Control')
    raw = fetch(url, headers=headers)
    self.response.headers["Content-Type"] = "text/javascript"
    self.response.out.write('%s("' % callback)
    self.response.out.write('data:%s;base64,' % escapejs(raw.headers.get('Content-Type', '')))
    self.response.out.write(base64.b64encode(raw.content))
    self.response.out.write('")')

def main():
  application = webapp.WSGIApplication([
    ('/proxy', ProxyHandler),
    ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()

"""
You want to be able to control or interact with your program remotely over
the network using a simple REST_based interface. However, you don't want to
do it by installing a full-fledged web programming framework.
"""

# Create a tiny library based on the WSGI standard.
# See PEP-3333 for more info: https://peps.python.org/pep-3333/

import cgi
import time
from urllib.request import urlopen
from wsgiref.simple_server import make_server
from threading import Thread

_hello_resp = """\
<html>
    <head>
    <title>Hello {name}</title>
    </head>
    <body>
    <h1>Hello {name}!</h1>
    </body>
</html>
"""

_localtime_resp = """\
<?xml version="1.0"?>
<time>
  <year>{t.tm_year}</year>
  <month>{t.tm_mon}</month>
  <day>{t.tm_mday}</day>
  <hour>{t.tm_hour}</hour>
  <minute>{t.tm_min}</minute>
  <second>{t.tm_sec}</second>
</time>"""


def notfound_404(environ, start_response):
    start_response("404 Not Found", [("Content-type", "text/plain")])
    return [b"Not Found"]


class PathDispatcher:
    def __init__(self):
        self.pathmap = {}

    def __call__(self, environ, start_response):
        path = environ["PATH_INFO"]
        params = cgi.FieldStorage(environ["wsgi.input"], environ=environ)
        method = environ["REQUEST_METHOD"].lower()
        environ["params"] = {key: params.getvalue(key) for key in params}
        handler = self.pathmap.get((method, path), notfound_404)
        return handler(environ, start_response)

    def register(self, method, path, function):
        self.pathmap[method.lower(), path] = function


def hello_world(environ, start_response):
    start_response("200 OK", [("Content-type", "text/html")])
    params = environ["params"]
    resp = _hello_resp.format(name=params.get("name"))
    yield resp.encode("utf-8")


def localtime(environ, start_response):
    start_response("200 OK", [("Content-type", "application/xml")])
    resp = _localtime_resp.format(t=time.localtime())
    yield resp.encode("utf-8")


def serve():
    dispatcher = PathDispatcher()
    dispatcher.register("GET", "/hello", hello_world)
    dispatcher.register("GET", "/localtime", localtime)

    # Launch a basic server to handle requests until process is killed
    # Alternatively, use https.handle_request() to handle a single request
    httpd = make_server("", 8000, dispatcher)
    print("serving on port 8000...")
    httpd.serve_forever()


def main():
    server = Thread(target=serve, daemon=True)
    server.start()
    response = urlopen("http://localhost:8000/hello?name=Chris")
    print(response.read().decode())
    response = urlopen("http://localhost:8000/localtime")
    print(response.read().decode())


if __name__ == "__main__":
    main()

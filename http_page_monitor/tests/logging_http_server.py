""" Tests the PageWatcher class to ensure that
    requests are being made and compared properly """
from http.server import HTTPServer, BaseHTTPRequestHandler
from random import randint
from datetime import datetime
from threading import Thread


class UpdatingWebsite(BaseHTTPRequestHandler):
    """ This class is an HTTP server that continously
        updates some pages for testing purposes"""

    def do_GET(self):
        """ Return a page """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path == "/every2":
            if self.server.request_count % 2:
                self.wfile.write("Response 2".encode('utf-8'))
            else:
                self.wfile.write("Response 1".encode('utf-8'))

        else:
            self.wfile.write("Response".encode('utf-8'))
            # Log the request and increment the request counter
        self.server.log(datetime.now())
        self.server.request_count += 1
        return 0


class LoggingHTTPServer(HTTPServer):
    """ This is an extension to the base HTTPServer that
        simply provides a way for the request handler to
        log things. """
    def __init__(self, *args, **kwargs):
        self.reset_log()
        self.running = False
        super().__init__(*args, **kwargs)

    def log(self, data):
        """ Log some data, any data. """
        self.data_log.append(data)

    def reset_log(self):
        """ Reset the entire log """
        self.data_log = []
        self.request_count = 0

    def generate_address(self, route):
        """ Returns a base address string used for
            accessing this server such as "localhost:5000" """
        return "http://localhost:" + str(self.server_address[1]) + route

    def handle_requests(self):
        """ Starts up the server. Can be stopped by calling shutdown() """
        #t = Thread(target=self.handle_some_requests, args=(request_count,))
        t = Thread(target=self.serve_forever)
        t.start()
        return t


def setup_logging_server():
    """ Gets a testing server ready to go
        and returns the port being used"""
    port_to_try = 5000

    # Try to get an open port 32 times
    for _ in range(0, 32):
        try:
            server = LoggingHTTPServer(('', port_to_try), UpdatingWebsite)
            return server
        except OSError as err:
            if "[Errno 98] Address already in use" not in str(err):
                raise

        port_to_try = randint(2**14, 2**15)

    raise OSError("Couldn't find an open port. "
                  "How many open ports do you have?")

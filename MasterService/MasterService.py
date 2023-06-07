from http.server import BaseHTTPRequestHandler

from MasterService.Logging import *
from MasterService.MasterDomain import MasterDomain
import json

class MasterService(BaseHTTPRequestHandler):
    def _set_response(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        service_log("GET request!")
        domain = MasterDomain()
        response = ""
        if self.path == "/get-messages":
            msg = domain.get_messages()
            response = json.dumps({"messages":msg})
            self._set_response(200)
        else:
            self._set_response(404)
        self.wfile.write(response.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        service_log("POST request! With new message: " + post_data.decode('utf-8'))
        domain = MasterDomain()

        if self.path == "/add-message":
            if domain.add_message(data["message"]):
                self._set_response(200)
            else:
                self._set_response(500)
        elif self.path == "/register":
            domain.add_client(data["ip"]+":"+data["port"])
            self._set_response(200)
        else:
            self._set_response(404)

        self.wfile.write("".encode('utf-8'))
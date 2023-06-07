import tornado
from MasterService.Logging import *
from MasterService.MasterDomain import MasterDomain
import tornado.ioloop
import tornado.web
import json
from tornado.gen import coroutine

import json

class AddMessageHandler(tornado.web.RequestHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
            service_log("POST request! With new message: " + data["message"])
            domain = MasterDomain()
            res = yield domain.add_message(data["message"], data["write-concern"])
            if (res):
                self.set_status(200)
            else:
                self.set_status(500)
            self.write("")
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))

class RegisterHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            service_log("POST request! With new message: " + data["ip"]+":"+data["port"])
            domain = MasterDomain()

            domain.add_client(data["ip"]+":"+data["port"])
            self.set_status(200)
            self.write("")
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))

class GetMessageHandler(tornado.web.RequestHandler):
    @coroutine
    def get(self):
        try:
            service_log("GET request!")
            domain = MasterDomain()
            self.write(json.dumps((yield domain.get_messages())))
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))

# class MasterService(tornado.web.RequestHandler):
#     def _set_response(self, code):
#         self.send_response(code)
#         self.send_header('Content-type', 'text/plain')
#         self.end_headers()

#     async def get(self):
#         service_log("GET request!")
#         domain = MasterDomain()
#         response = ""
#         if self.path == "/get-messages":
#             response = json.dumps(domain.get_messages())
#             self._set_response(200)
#         else:
#             self._set_response(404)
#         self.write(response.encode('utf-8'))

#     async def post(self):
#         content_length = int(self.headers['Content-Length'])
#         post_data = self.rfile.read(content_length)
#         data = json.loads(post_data)
#         service_log("POST request! With new message: " + post_data.decode('utf-8'))
#         domain = MasterDomain()

#         if self.path == "/add-message":
#             if domain.add_message(data["message"], data["write-concern"]):
#                 self._set_response(200)
#             else:
#                 self._set_response(500)
#         elif self.path == "/register":
#             domain.add_client(data["ip"]+":"+data["port"])
#             self._set_response(200)
#         else:
#             self._set_response(404)

#         self.write("".encode('utf-8'))
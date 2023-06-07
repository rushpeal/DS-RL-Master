from http.server import HTTPServer
import argparse
import asyncio
import tornado

from MasterService.Logging import *
import MasterService.Constants as constants
from MasterService.AddressHelper import AddressHelper
from MasterService.Constants import ConfigKeys
from MasterService.MasterDomain import MasterDomain
from MasterService.MasterService import AddMessageHandler, GetMessageHandler, RegisterHandler

class MasterApp:
    def __init__(self):
        configure_logging(constants.SERVICE_NAME)

        self.arg_parser = argparse.ArgumentParser(
                    prog = constants.SERVICE_NAME,
                    description = 'Service to log messages')
        self.add_args_to_parser()
        
        self.config = dict()
        self.config[ConfigKeys.RETRIES_TO_SECONDARY] = 5
        self.parse_args()

    def parse_args(self):
        args = self.arg_parser.parse_args()
        self.config[ConfigKeys.PORT] = args.port
        if args.retry is not None:
            self.config[ConfigKeys.RETRIES_TO_SECONDARY] = args.retry

    def add_args_to_parser(self):
        self.arg_parser.add_argument('-p', '--port', type=int) 
        self.arg_parser.add_argument('-r', '--retry', type=int) 

    def run(self):
        addr_helper = AddressHelper()
        MasterDomain(addr_helper, self.config[ConfigKeys.RETRIES_TO_SECONDARY])

        app = tornado.web.Application([
            (r"/add-message", AddMessageHandler),
            (r"/register", RegisterHandler),
            (r"/get-messages", GetMessageHandler),
        ])

        server_address = ('', self.config[ConfigKeys.PORT])
        app_log('Starting httpd at ' + str(server_address))

        app.listen(self.config[ConfigKeys.PORT])

        tornado.ioloop.IOLoop.current().start()
        app_log('Stopping httpd...')
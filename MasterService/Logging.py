import logging 
import time
import os
import sys

my_logger = logging.Logger("service-logger", logging.INFO)


def app_log(msg):
    my_logger.info(msg, extra={
        'log_layer': 'App'
    })

def domain_log(msg):
    my_logger.info(msg, extra={
        'log_layer': 'Domain'
    })

def service_log(msg):
    my_logger.info(msg, extra={
        'log_layer': 'Service'
    })

def configure_logging(service_name):
    FORMAT = logging.Formatter('[' + service_name + '][%(log_layer)s][%(asctime)s]: %(message)s')

    file_name = "{0}/{1}-{2}.log".format('logs/', service_name, time.ctime().replace(' ', '_').replace(':', '-'))
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    fileHandler = logging.FileHandler(file_name)
    fileHandler.setFormatter(FORMAT)
    my_logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(FORMAT)
    my_logger.addHandler(consoleHandler)
    app_log('Initialized logging for ' + service_name)
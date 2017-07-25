import logging
import datetime

enabled = False

def log(message):
    if enabled:
        time = str(datetime.datetime.now())
        logging.debug(time + ': ' + message)
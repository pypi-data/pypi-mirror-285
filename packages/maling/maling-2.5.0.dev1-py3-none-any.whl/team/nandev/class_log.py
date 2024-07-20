################################################################
"""
 Mix-Userbot Open Source . Maintained ? Yes Oh No Oh Yes Ngentot
 
 @ CREDIT : NAN-DEV
"""
################################################################

import logging
import os
import sys


class ConnectionHandler(logging.Handler):
    def emit(self, record):
        for ah in ["OSError", "socket"]:
            if ah in record.getMessage():
                os.execl(sys.executable, sys.executable, "-m", "Mix")


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s] - %(name)s - %(message)s", "%d-%b %H:%M")
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(formatter)
connection_handler = ConnectionHandler()

logger.addHandler(stream_handler)
logger.addHandler(connection_handler)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.INFO)

LOGS = logging.getLogger("Mix-Userbot")

def LOGG(name: str) -> logging.Logger:
    return logging.getLogger(name)
    
LOGGER = LOGG("Mix-Userbot")
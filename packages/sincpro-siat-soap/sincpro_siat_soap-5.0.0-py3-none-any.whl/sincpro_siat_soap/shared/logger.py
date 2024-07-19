import logging
import os

import logzero

LOGGING_LEVEL = os.getenv("SP_SIAT_LOG_LEVEL")

logzero.loglevel(logging.INFO)

if LOGGING_LEVEL == "DEBUG":
    logzero.loglevel(logging.DEBUG)

logzero.logfile("/tmp/sp_siat.log")
logger = logzero.logger

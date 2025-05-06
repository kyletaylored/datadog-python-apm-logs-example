import os
import logging
import random
from celery import Celery
from logging.handlers import SysLogHandler
from pythonjsonlogger import jsonlogger

# Celery setup
app = Celery('tasks', broker='redis://localhost:6379/0')

MESSAGES = [
    "User signed in",
    "Cache cleared",
    "Email sent",
    "Session expired",
    "Data synced",
    "External API called",
]

# ENV CONFIG
LOG_FORMAT = os.getenv("LOG_FORMAT", "json").lower()        # json | text
# stdout | file | syslog
LOG_OUTPUT = os.getenv("LOG_OUTPUT", "stdout").lower()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/tmp/celery_tasks.log")
# Or ('localhost', 514) for UDP
SYSLOG_ADDRESS = os.getenv("SYSLOG_ADDRESS", "/dev/log")

include_dd_fields = os.getenv("LOG_CORRELATED", "true").lower() == "true"

# Choose format based on LOG_FORMAT and LOG_CORRELATED
if include_dd_fields:
    text_format = (
        '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
        '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
        'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s'
    )

    json_format = (
        '%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d '
        '%(message)s %(dd.service)s %(dd.env)s %(dd.version)s '
        '%(dd.trace_id)s %(dd.span_id)s'
    )
else:
    text_format = (
        '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
    )

    json_format = (
        '%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s'
    )


formatter = (
    jsonlogger.JsonFormatter(json_format)
    if LOG_FORMAT == "json"
    else logging.Formatter(text_format)
)

# LOGGER SETUP
logger = logging.getLogger("celery_logger")
logger.setLevel(logging.INFO)
logger.propagate = False
logger.handlers.clear()

# HANDLER SETUP
if LOG_OUTPUT == "stdout":
    handler = logging.StreamHandler()

elif LOG_OUTPUT == "file":
    handler = logging.FileHandler(LOG_FILE_PATH)

elif LOG_OUTPUT == "syslog":
    try:
        # Try UNIX socket (Linux/macOS)
        handler = SysLogHandler(address=SYSLOG_ADDRESS)
    except Exception:
        # Fallback: try UDP
        handler = SysLogHandler(address=('localhost', 514))

else:
    raise ValueError("LOG_OUTPUT must be 'stdout', 'file', or 'syslog'")

handler.setFormatter(formatter)
logger.addHandler(handler)


@app.task
def log_something():
    """
    Log a random message.
    """
    message = random.choice(MESSAGES)
    logger.info(message)
    return message

# -*- encoding: utf-8 -*-
'''
@File    :   logger.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

import sys, os, logging
from loguru import logger
from datetime import datetime
from pprint import pformat
from loguru._defaults import LOGURU_FORMAT

def parse_log_level_value(v):
    if not v:
        v = "DEBUG"
    v = logging.getLevelName(v)
    return v

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string

def init_logging(project_name, log_level):
    """
    Replaces logging handlers with a handler for using the custom handler.
        
    WARNING!
    if you call the init_logging in startup event function, 
    then the first logs before the application start will be in the old format
    >>> app.add_event_handler("startup", init_logging)
    stdout:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [11528] using statreload
    INFO:     Started server process [6036]
    INFO:     Waiting for application startup.
    2020-07-25 02:19:21.357 | INFO     | uvicorn.lifespan.on:startup:34 - Application startup complete.
    
    """

    # disable handlers for specific uvicorn loggers
    # to redirect their output to the default uvicorn logger
    # works with uvicorn==0.11.6
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.configure(handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}])

    # logger save dir
    logger_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logger_dir):
        os.makedirs(logger_dir)

    run_time = datetime.now().strftime("%Y_%m_%d")

    logger_file_name = f"{project_name}_{run_time}.log"

    logger_path = os.path.join(logger_dir, logger_file_name)
    log_level = parse_log_level_value(log_level)

    # configure loguru
    logger.add(logger_path, 
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} - [process: {process} - thread: {thread}][{module} - {file}:{line} - {function}] - {level} - {message}", 
        encoding='utf-8', filter="", level=int(log_level), rotation="100 MB", compression="zip", enqueue=True, colorize=True)
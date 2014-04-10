from logging import getLogger, StreamHandler, Formatter, FileHandler, DEBUG
from logging.handlers import NTEventLogHandler, SysLogHandler

def get_logger(component):
    logger = getLogger(component)
    logger.setLevel(DEBUG)

    return logger

def get_formatter():
    return Formatter('%(asctime)-15s %(module)s : %(levelname)s : %(message)s')

def add_console_handler(logger):
    ch = StreamHandler()
    ch.setLevel(DEBUG)
    ch.setFormatter(get_formatter())

    logger.addHandler(ch)

def add_file_handler(logger):
    from os import path, mkdir

    if not path.exists('./logs') :
        mkdir('./logs')


    fh = FileHandler('./logs/GISMOH.log', 'a+')
    fh.setLevel(DEBUG)
    fh.setFormatter(get_formatter())

    logger.addHandler(fh)

def add_win_event_log_handler(logger):
    nh = NTEventLogHandler('GISMOH')
    nh.setLevel(DEBUG)
    nh.setFormatter(get_formatter())

    logger.addHandler(nh)

def add_sys_log_handler(logger):
    sh = SysLogHandler()
    sh.setLevel(DEBUG)
    sh.setFormatter(get_formatter())

    logger.addHandler(sh)



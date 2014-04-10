from nose.tools import raises, with_setup
import datetime
import unittest

from modules.Logging import *

class logging_test(unittest.TestCase):
    def test_consoleLog(self):
        log = get_logger(__name__)
        add_console_handler(log)
        log.debug('test')

        assert True

    def test_fileLog(self):
        log = get_logger(__name__)
        add_file_handler(log)
        log.debug('test')

        assert True
    def test_winLog(self):
        log = get_logger(__name__)
        add_win_event_log_handler(log)
        log.debug('test')

        assert True
    def test_sysLog(self):
        log = get_logger(__name__)
        add_sys_log_handler(log)
        log.debug('test')

        assert True

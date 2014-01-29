from nose.tools import raises, with_setup
import datetime
import unittest

from store.Store import SQLiteStore, Location

DBFILENAME = 'gismoh_test'

class sqlite_test(unittest.TestCase):
    def test_connect(self):
        st = SQLiteStore(DBFILENAME)
        assert st is not None
        
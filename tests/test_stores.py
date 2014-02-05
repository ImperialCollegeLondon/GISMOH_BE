from nose.tools import raises, with_setup
import datetime
import unittest

from store.SQL import SQLiteStore
from store.Store import Patient, Location, Mapping

DBFILENAME = 'gismoh_test'

class sqlite_test(unittest.TestCase):
    def test_connect(self):
        st = SQLiteStore(DBFILENAME)
        assert st is not None
        
    def test_get_arg(self):
        st = SQLiteStore(DBFILENAME)

        clause = st.get_where_clause(Patient, 'x')

        print clause

        assert clause== 'x = ?'


    def test_mapper(self):
        _map = Mapping()
        
        _map.add_object('Patient', 'Patient', {
            'uniq_id': 'patient_id',
            'nhs_number' : 'nhsNumber',
            'sex' : 'sex',
            'date_of_birth' : 'dob',
            'postcode' : 'postcode'
        })
        
        assert _map.object_to_db('Patient', 'nhs_number') == 'nhsNumber'
        
    def test_create_query(self):
        _map = Mapping()
        
        _map.add_object('Patient', 'Patient', {
            'uniq_id': 'patient_id',
            'nhs_number' : 'nhsNumber',
            'sex' : 'sex',
            'date_of_birth' : 'dob',
            'postcode' : 'postcode'
        })
        
        pat = Patient()
        pat.nhs_number = '111-111-1111'
        pat.sex='F'
        pat.date_of_birth = datetime.datetime(2014, 1, 29)
        
        st = SQLiteStore(DBFILENAME, _map)
        try:
            st.save(pat)
        except Exception:
            assert True
        
        pat2 = st.get(Patient, '111-111-1111')
        for fld in pat.__dict__:
            print fld
            print type(getattr(pat,fld)), type(getattr(pat2, fld))
            assert getattr(pat,fld) == getattr(pat2, fld)

    def test_find(self):
        _map = Mapping()

        _map.add_object('Patient', 'Patient', {
            'uniq_id': 'patient_id',
            'nhs_number' : 'nhsNumber',
            'sex' : 'sex',
            'date_of_birth' : 'dob',
            'postcode' : 'postcode'
        })

        st = SQLiteStore(DBFILENAME, _map)

        pats = st.find(Patient, {'field' : 'sex', 'op' : '=', 'value' : 'F'})

        print len(pats)

        assert len(pats) == 1

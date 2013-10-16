import store.Store as Store
import couchbase
from nose.tools import raises, with_setup
import datetime
import unittest

class main_test(unittest.TestCase):
    con = None
    
    def test_connect(self):
        con = Store.Store('GISMOH', 'gismoh2')
        assert type(con.db) == couchbase.connection.Connection 
    
    @raises(couchbase.connection.BucketNotFoundError)
    def test_bad_bucket(self):
        con = Store.Store('bad_bucket')
        
    @raises(couchbase.connection.AuthError)
    def test_auth_fail(self):
        con = Store.Store('GISMOH', 'boo')
        
    def test_format_nhs_number(self):
        assert Store.Patient.format_nhs_number('1234567890') == '123-456-7890'
        
    def test_validate_nhs_number_bad(self):
        assert not Store.Patient.validate_nhs_number('1234567890')
     
    def test_validate_nhs_number_good(self):   
        from utils.Modulus11 import Mod11
        newnum = '123456789'
        print Mod11.calculate(newnum)
        assert Store.Patient.validate_nhs_number(newnum + Mod11.calculate(newnum))
        assert Store.Patient.validate_nhs_number('123456789X')

    def test_add_patientself(self):
        con = Store.Store('GISMOH', 'gismoh2')
        pat = Store.Patient()
        pat.uniq_id = 'Pat1'
        pat.nhs_number = '123456789X'
        pat.sex = 'M'
        pat.dob = datetime.date(1970, 1, 1)
        
        con.save(pat)

    def test_get_patientself(self):
        con = Store.Store('GISMOH', 'gismoh2')
        res = con.fetch('Patient:Pat1')
        assert res.value['uniq_id'] == 'Pat1' 
        
    @raises(couchbase.connection.NotFoundError)
    def test_get_patientself(self):
        con = Store.Store('GISMOH', 'gismoh2')
        res = con.fetch('Patient:Pat2')
                
    def test_from_dict_nomap(self):
        _td = { nhs_number : '123456789X', sex : 'M' }
        pat = Store.Patient()
        pat.from_dict(_td)
        assert pat.nhs_number == '123456789X'
        assert pat.sex == 'M'
        
    def test_from_dict_nomap(self):
        _td = { 'nhsno' : '123456789X', 'gender' : 'M' }
        pat = Store.Patient()
        pat.from_dict(_td, { 'nhsno' : 'nhs_number', 'gender' : 'sex'})
        assert pat.nhs_number == '123456789X'
        assert pat.sex == 'M'
        
        
        
        
import interfaces.scbu as ds
from unittest import TestCase
from store.Store import CouchbaseStore as Store, Location, Patient, Result
from modules.Antibiogram import Antibiogram 
from nose.tools import raises, with_setup

CB_SERVER = '127.0.0.1'
CB_BUCKET = 'GISMOH'
CB_ACCESS = 'gismoh2'

class SCBU_Tests(TestCase):
    def test_create_interface(self):
        con = Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        _if = ds.SCBU_Importer('/Users/Chris/Documents/Addenbrookes Project/SCBU.xlsx', con)
            
    def test_do_import(self):
        con = Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        _if = ds.SCBU_Importer('/Users/Chris/Documents/Addenbrookes Project/SCBU.xlsx', con)
        _if.read_admissions()
        _if.read_isolates()
            
    def test_get_patient(self):
        con = Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        pat = Patient.get_by_key(con, '1.0')
        assert pat.uniq_id == 1
            
    def test_get_location(self):
        con = Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        pat = Location.get_by_key(con, '229.0:1320343200.0')
        assert pat.patient_id == 229.0
           
    def test_get_result(self):
            
        con = Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        res = Result.get_by_key(con, '2495.0:Disc Diffusion:2011-01-10')

class Antibiogram_test(TestCase):

    def setUp(self):
         self.ab1 ={ 'result' :  [
       {
           "SIR": "R",
           "Antibiotic": "Flucloxacillin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Ciprofloxacin"
       },
       {
           "SIR": "R",
           "Antibiotic": "Erythromycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "FusidicAcid"
       },
       {
           "SIR": "S",
           "Antibiotic": "Gentamicin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Tetracycline"
       },
       {
           "SIR": "S",
           "Antibiotic": "Vancomycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Mupirocin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Rifampicin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Neomycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Linezolid"
       },
       {
           "SIR": "S",
           "Antibiotic": "Chloramphenicol"
       }
    ]}
         self.ab2 ={ 'result' : [
       {
           "SIR": "R",
           "Antibiotic": "Flucloxacillin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Ciprofloxacin"
       },
       {
           "SIR": "R",
           "Antibiotic": "Erythromycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "FusidicAcid"
       },
       {
           "SIR": "S",
           "Antibiotic": "Gentamicin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Tetracycline"
       },
       {
           "SIR": "S",
           "Antibiotic": "Vancomycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Mupirocin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Rifampicin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Neomycin"
       },
       {
           "SIR": "S",
           "Antibiotic": "Linezolid"
       },
       {
           "SIR": "S",
           "Antibiotic": "Chloramphenicol"
       }
   ]}
    
    def test_compare_same(self):
       
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        assert _abm.compare(self.ab1, self.ab2) == 1
    
    def test_compare_one_diff(self):
        
        self.ab2['result'][0]['SIR'] = 'S'        
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        res = _abm.compare(self.ab1, self.ab2) 
        assert res ==  (1.0 - (1.0/12))
        
    def test_compare_one_gap(self):
        
        self.ab2['result'][0]['SIR'] = 'I'        
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        res = _abm.compare(self.ab1, self.ab2)  
        assert res ==  (1.0 - (1.0/24.0))
    
    def test_compare_two_gap(self):
        
        del self.ab2['result'][0]  
        del self.ab2['result'][5]    
        
           
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        res = _abm.compare(self.ab1, self.ab2)  
        assert res ==  (1.0 - (1.0/12.0))    
        
    def test_get_nearest_default(self):
        
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        _abl = _abm.get_nearest(self.ab1)
        
        for ab in _abl:
            assert ab['similarity'] == 1

    def test_get_nearest_n(self):
        
        _abm = Antibiogram(Store(CB_BUCKET, CB_ACCESS, CB_SERVER))
        _abl = _abm.get_nearest(self.ab1, n = 5)
        
        assert len(_abl) <= 5
        
        for ab in _abl:
            assert ab['similarity'] == 1


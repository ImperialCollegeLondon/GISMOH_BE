from modules.Location import LocationInterface
from store import Store
from unittest import TestCase

import datetime

CB_SERVER = '127.0.0.1'
CB_BUCKET = 'GISMOH'
CB_ACCESS = 'gismoh2'

class LocationIFTests(TestCase):
    
    def setUp(self):
        self.con = Store.Store(CB_BUCKET, CB_ACCESS, CB_SERVER)
        self._if = LocationInterface(self.con)
        
    def test_get_by_id(self):
        loc = Store.Location.get_by_key(self.con, '1.0:1293479100.0')
        assert loc.patient_id == 1.0
        assert loc.ward == 'SCBU'
         
    def test_get_overlaps(self):
        loc = Store.Location.get_by_key(self.con, '1.0:1293479100.0')
          
        overlaps = self._if.get_overlaps_with_location(loc)
          
        assert len(overlaps) > 0
          
    def test_overlaps_length(self):
        _doc = self.con.fetch('Patient:1.0')
  
          
        pat = Store.Patient()
        pat.from_dict(_doc.value)
          
        overlaps = self._if.get_overlaps_with_patient(pat)
          
        for key in overlaps.keys():
            loc_a = Store.Location.get_by_key(self.con, key)
              
            for loc_b in overlaps[key]:
                assert loc_a.ward == loc_b.ward
                gap = min((loc_b.left - loc_a.arrived).total_seconds(), (loc_a.left - loc_b.arrived).total_seconds())
                assert gap > 0
                  
    def test_get_location_at_date(self):
        qdate = datetime.datetime(2012, 1, 1, 00, 00, 00)
        
        p_list = []
        
        for loc in Store.Location.get_locations_at(self.con, qdate):
            
            assert loc.arrived < qdate
            assert loc.left is None or loc.left > qdate 
            assert not p_list.__contains__(loc.patient_id) 
            
            p_list.append(loc.patient_id)
            
    def test_get_admission_at_date(self):
        qdate = datetime.datetime(2012, 1, 1, 00, 00, 00)
        
        p_list = []
        a_list = []
        
        for adm in Store.Admission.get_admissions_at(self.con, qdate):
            print adm.patient_id, adm.get_key()
            assert adm.start_date < qdate
            assert adm.end_date is None or adm.end_date > qdate 
            assert not a_list.__contains__(adm.get_key()) 
            assert not p_list.__contains__(adm.patient_id) 
            print p_list
            p_list.append(adm.patient_id)
            a_list.append(adm.get_key())

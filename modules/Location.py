from store import Store
from datetime import datetime

class LocationInterface(object):
    def __init__(self, store):
        self.store = store
    
    ## Get overlaps with a location
    # @param location Store.Location:     
    def get_overlaps_with_location(self, location):
        a = location
        
        q = self.store.create_query()
        q.mapkey_single = a.ward
        
        overlaps = []
        
        for b_key in self.store.get_next_from('Location_by_ward', query = q):
            b_dict = self.store.fetch(b_key.docid).value
            b = Store.Location()
            b.from_dict(b_dict)
            
            if min(((a.left if a.left is not None else datetime.now()) - b.arrived).total_seconds(), ((b.left if b.left is not None else datetime.now())  - a.arrived).total_seconds()) > 0 :
                overlaps.append(b)
                
        return overlaps
    
    def get_overlaps_with_patient(self, patient, date_from = None, date_to = None):
        q = self.store.create_query()
        q.mapkey_single = patient.uniq_id
        
        overlaps = {}
        
        for l_key in self.store.get_next_from('Location_by_patient_id', query = q):
            l = Store.Location.get_by_key(self.store, str(l_key.docid).replace('Location:', ''))
            _lst = self.get_overlaps_with_location(l)
            overlaps[l.get_key()] = _lst
        
        
        return overlaps
            
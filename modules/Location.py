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
        
        b_keys = [b_key.docid for b_key in self.store.get_next_from('Location_by_ward', query = q)]

        for b in self.store.fetch_objects(b_keys) :
            if min(((a.left if a.left is not None else datetime.now()) - b.arrived).total_seconds(), ((b.left if b.left is not None else datetime.now())  - a.arrived).total_seconds()) > 0 :
                overlaps.append(b)
                
        return overlaps
    
    def get_overlaps_with_patient(self, patient, date_from = None, date_to = None):
        q = self.store.create_query()
        q.mapkey_single = patient.uniq_id
        
        overlaps = {}
        
        keys = [l.docid for l in self.store.get_next_from('Location_by_patient_id', query = q)]

        patient_locations = self.store.fetch_objects(keys)
        
        for loc in patient_locations:
            _lst = self.get_overlaps_with_location(loc)
            overlaps[loc.get_key()] = _lst
        
        return overlaps

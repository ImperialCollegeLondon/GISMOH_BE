from store import Store
from datetime import datetime

class LocationInterface(object):
    def __init__(self, store):
        self.store = store
    
    ## Get overlaps with a location
    # @param location Store.Location:     
    def get_overlaps_with_location(self, location):
        a = location
        overlaps = []
        
        b_list = self.store.find(Store.Location, {'field' : 'ward', 'op' : '=', 'value' : a.ward})

        for b in b_list :
            if min(((a.left if a.left is not None else datetime.now()) - b.arrived).total_seconds(), ((b.left if b.left is not None else datetime.now())  - a.arrived).total_seconds()) > 0 :
                overlaps.append(b)
                
        return overlaps
    
    def get_overlaps_with_patient(self, patient, date_from = None, date_to = None):
        patient_locations = self.store.find(Store.Location, {'field' : 'patient_id', 'op' : '=', 'value' : patient.uniq_id})
        overlaps = {}
        
        for loc in patient_locations:
            _lst = self.get_overlaps_with_location(loc)
            overlaps[loc.get_key()] = _lst
        
        return overlaps

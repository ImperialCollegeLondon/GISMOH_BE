"""
GISMOH store
"""
from couchbase import Couchbase, views

import datetime
from time import mktime

class Store:
    db = None
    
    def __init__(self, bucket, password=None):
        self.db = Couchbase.connect(bucket=bucket, password=password)
    
    def save(self, obj):
        self.db.set(u"%s:%s" % (obj.get_type() ,obj.get_key()), obj.get_dict())
    
    def fetch(self, key):
        return self.db.get(key)
      
    def get_view(self, name, query = None, limit = None, dev = False):
        
        doc = 'gismoh'
        
        if dev:
            doc = 'dev_gismoh'
        _view = views.iterator.View(self.db, doc, name, query = query)
        return _view
    
    def get_next_from(self, name, limit=None, dev = False):
        
        _view = self.get_view(name, limit, dev)
        
        for doc in _view:
            yield doc

    def get_from_view_by_key(self, name, key):
        
        _query = views.params.Query()
        _query.mapkey_single = key
        _view = self.get_view(name, _query)
        
        return _view
        
    
class GISMOH_Object(object):

    def get_key(self):
        pass
    
    def get_type(self):
        return type(self).__name__
    
    def get_dict(self):
        obj_dict = self.__dict__
        
        for prop in obj_dict:
            if type(obj_dict[prop]) == datetime.date:
                obj_dict[prop] = obj_dict[prop].strftime('%Y-%m-%d')
            elif type(obj_dict[prop]) == datetime.datetime:
                obj_dict[prop] = obj_dict[prop].strftime('%Y-%m-%d %H:%M:%s')
            elif type(obj_dict[prop]) == datetime.time:
                 obj_dict[prop] = obj_dict[prop].strftime('%H:%M:%s')
                 
        obj_dict['type'] = self.get_type()
        
        return obj_dict
    
    def from_dict(self, _dict, _map = None):
        if _map is None :
            get_key = lambda key : key
        else:
            get_key = lambda key : _map[key] if _map.has_key(key) else None
        
        for key in _dict.keys():
            _mk = get_key(key)
            
            if _mk is not None and _dict.has_key(key):
                setattr(self, _mk , _dict[key])      
        

class Admission(GISMOH_Object):
    uniq_id = None
    start_date = None
    end_date = None
    patient_id = None
    
    def get_key(self):
        return "%s:%s" % (self.patient_id, mktime(self.start_date.timetuple()))
    

class Isolate(GISMOH_Object):
    lab_number = None
    patient_id = None
    date_taken = None
    meta_tags = None
    
    def get_key(self):
        return self.lab_number
    
class Location(GISMOH_Object):
    ward= None
    specialty = None
    arrived = None
    left = None
    patient_id = None
    
    def get_key(self):
         return "%s:%s" % (self.patient_id, mktime(self.arrived.timetuple()))

class Patient(GISMOH_Object):
    """
    Class to store a patient
    """
    ## internal GISMOH idnetifier
    uniq_id = None
    ##NHS Number of the patienr
    nhs_number = None
    ## Patient's sex
    sex = None
    ## Patient's date of birth
    date_of_birth = None
    
    def __init__(self):
        pass
    
    ### return the anonymised unique identifier of the Patient
    def get_key(self):
        return self.uniq_id
    
    ## Get NHS Number in a the format 000-000-0000
    @staticmethod
    def format_nhs_number(raw_number):
        from re import match
        
        if type(raw_number) == float:
            raw_number = str(int(raw_number))
        elif type(raw_number) != str:
            raw_number = str(raw_number)
              
        if match('\d{3}-\d{3}-\d{3}[\dX]', raw_number):
            return raw_number
        elif match('\d{9}[\dX]', raw_number):
            return '%s-%s-%s' % (raw_number[0:3], raw_number[3:6], raw_number[6:]) 
        else:
            raise Exception('NHS Number must be in the format 000-000-0000 or a 10 digit number')
        

    @staticmethod
    def validate_nhs_number(nhs_number):
        from utils.Modulus11 import Mod11
        
        return Mod11.check(nhs_number)
    
##Class that describes a test result such as an antibiogram
class Result(GISMOH_Object):
    test_type = None
    result = None
    result_type = None
    test_date = None
    isolate_id = None
    
    def get_key(self):
        return '%s:%s:%s' % (self.isolate_id, self.test_type, self.test_date.strftime('%Y-%m-%d'))

"""
GISMOH store
"""
from couchbase import Couchbase, views

import datetime
from time import mktime

## Connection to a database
class Store:
    db = None
    
    def __init__(self, bucket, password=None):
        self.db = Couchbase.connect(bucket=bucket, password=password)
    
    def save(self, obj):
        self.db.set(u"%s:%s" % (obj.get_type() ,obj.get_key()), obj.get_dict())
    
    def fetch(self, key):
        return self.db.get(key)
      
    def get_view(self, name, query = None, limit = None, dev = True):
        
        doc = 'gismoh'
        
        if dev:
            doc = 'dev_gismoh'
        _view = views.iterator.View(self.db, doc, name, query = query)
        return _view
    
    def create_query(self):
        return views.params.Query(full_set=True)
    
    def get_next_from(self, name, limit=None, dev = False, query = None):
        
        _view = self.get_view(name, query, limit, dev = True)
        
        for doc in _view:
            yield doc

    def get_from_view_by_key(self, name, key):
        
        _query = views.params.Query()
        _query.mapkey_single = key
        _view = self.get_view(name, _query)
        
        return _view
    
        
    
class GISMOH_Object(object):

    def get_key(self):
        raise NotImplementedError()
    
    def get_type(self):
        return type(self).__name__
    
    def get_dict(self):
        obj_dict = self.__dict__
        
        for prop in obj_dict:
            if type(obj_dict[prop]) == datetime.date:
                obj_dict[prop] = obj_dict[prop].strftime('%Y-%m-%d')
            elif type(obj_dict[prop]) == datetime.datetime:
                obj_dict[prop] = obj_dict[prop].strftime('%Y-%m-%d %H:%M:%S')
            elif type(obj_dict[prop]) == datetime.time:
                 obj_dict[prop] = obj_dict[prop].strftime('%H:%M:%S')
                 
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
     
    @classmethod
    def get_by_key(cls, store, key):
         if type(key) == str or type(key) == unicode:
             key = key.replace('%s:' % cls.__name__, '')
         
         _doc = store.fetch(u'%s:%s'% (cls.__name__, key))
         obj = cls()
         obj.from_dict(_doc.value)
         return obj

class Admission(GISMOH_Object):
    uniq_id = None
    start_date = None
    end_date = None
    patient_id = None
    
    def get_key(self):
        return "%s:%s" % (self.patient_id, mktime(self.start_date.timetuple()))
    
    def from_dict(self, _dict, _map = None):
        super(Admission, self).from_dict(_dict, _map)
        
        if type(self.start_date) == unicode or type(self.start_date) == str:
            self.start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S')
         
        if type(self.end_date) == unicode or type(self.end_date) == str :
            self.end_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d %H:%M:%S')       
    
    @staticmethod
    def get_admissions_at(store, qry_date):
        """! 
            get a list of current admissions at qry_date
            @param qry_date
        """
        
        q_date_string = qry_date.strftime('%Y-%m-%d %H:%M:%S')
        
        qry = store.create_query()
        qry.mapkey_range=['', q_date_string]
        
        for l_res in store.get_view('Admission_by_start_Date',query=qry, dev=True):
            if l_res.value is None or l_res.value  > q_date_string :
                yield Admission.get_by_key(store, l_res.docid)    

class Isolate(GISMOH_Object):
    lab_number = None
    patient_id = None
    date_taken = None
    meta_tags = None
    species = None
    
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
     
    def from_dict(self, _dict, _map = None):
        super(Location, self).from_dict(_dict, _map)
        
        if type(self.arrived) == unicode or type(self.arrived) == str:
            self.arrived = datetime.datetime.strptime(self.arrived, '%Y-%m-%d %H:%M:%S')
         
        if type(self.left) == unicode or type(self.left) == str:
            self.left = datetime.datetime.strptime(self.left, '%Y-%m-%d %H:%M:%S')
    
    
    @staticmethod
    def get_locations_at(store, qry_date):
        """! 
            get locations of patients at date_str
            @param qry_date
        """
        
        q_date_string = qry_date.strftime('%Y-%m-%d %H:%M:%S')
        
        qry = store.create_query()
        qry.mapkey_range=['', q_date_string]
        
        for l_res in store.get_view('Location_by_start_date',query=qry, dev=True):
            if l_res.value is None or l_res.value  > q_date_string :
                yield Location.get_by_key(store, l_res.docid)

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

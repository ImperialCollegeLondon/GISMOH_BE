"""
GISMOH store
"""
import datetime
from time import mktime

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

class Mapping:
    _mapper = {}
    
    def __init__(self):
        _mapper = {}
    
    def object_to_db(self, _class, name):
        tbl = self._mapper[_class]
        return tbl['columns'][tbl['fields'].index(name)]
        
    def db_to_object(self, _class, name):
        tbl = self._mapper[_class]
        return tbl['fields'][tbl['columns'].index(name)]
    
    def get_fields(self, _class):
        return self._mapper[_class]['fields']
    
    def get_columns(self,_class):
        return self._mapper[_class]['columns']
    
    def get_table_name(self, _class):
        return self._mapper[_class]['table_name']
    
    def add_object(self, _class, table_name, mapping):
        _map = {
            'table_name' : table_name,
            'fields' : [],
            'columns' : []
        }
        
        for key in mapping:
            _map['fields'].append(key)
            _map['columns'].append(mapping[key])
            
        self._mapper[_class] = _map
          
## Base class describing functions shared by GISMOH objects   
class GISMOH_Object(object):

    def get_key_field(self):
        raise NotImplementedError()
    
    def get_key(self):
        raise NotImplementedError()
    
    def get_type(self):
        return type(self).__name__
    
    def get_dict(self):
        obj_dict = {}
        
        int_dict = self.__dict__
        
        for prop in int_dict:
            if type(int_dict[prop]) == datetime.date:
                obj_dict[prop] = int_dict[prop].strftime('%Y-%m-%d')
            elif type(int_dict[prop]) == datetime.datetime:
                obj_dict[prop] = int_dict[prop].strftime(TIME_FORMAT)
            elif type(int_dict[prop]) == datetime.time:
                 obj_dict[prop] = int_dict[prop].strftime('%H:%M:%S')
            else:
                obj_dict[prop] = int_dict[prop]
        #obj_dict['type'] = self.get_type() -- couchbase specific, so should be handled in the couchbase store function
        
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
         
         _doc = store.fetch(cls, key)
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
            self.start_date = datetime.datetime.strptime(self.start_date, TIME_FORMAT)
         
        if type(self.end_date) == unicode or type(self.end_date) == str :
            self.end_date = datetime.datetime.strptime(self.end_date, TIME_FORMAT)
    
    @staticmethod
    def get_admissions_at(store, qry_date):
        """! 
            get a list of current admissions at qry_date
            @param qry_date
        """
        q_date_string = qry_date.strftime(TIME_FORMAT)
        
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
    
    def from_dict(self, _dict, _map = None):
        super(Isolate, self).from_dict(_dict, _map)

        if type(self.date_taken) == unicode or type(self.date_taken) == str:
            self.date_taken = datetime.datetime.strptime(self.date_taken, TIME_FORMAT)

    @staticmethod
    def get_isolates_taken_between(store, from_date, to_date):
        q_start_string = from_date.strftime(TIME_FORMAT)
        q_end_string = to_date.strftime(TIME_FORMAT)

        qry = store.create_query()
        qry.mapkey_range=[q_start_string, q_end_string]
        qry.inclusive_end = True

        keys = [i_res.docid for i_res in store.get_view('isolates_by_date_taken', query=qry, dev=True)]
        return store.fetch_objects(keys)


class Location(GISMOH_Object):
    uniq_id = None
    ward= None
    specialty = None
    arrived = None
    left = None
    patient_id = None
    
    def get_key(self):
         return self.uniq_id
     
    def from_dict(self, _dict, _map = None):
        super(Location, self).from_dict(_dict, _map)
        
        if type(self.arrived) == unicode or type(self.arrived) == str:
            self.arrived = datetime.datetime.strptime(self.arrived, TIME_FORMAT)
         
        if type(self.left) == unicode or type(self.left) == str:
            self.left = datetime.datetime.strptime(self.left, TIME_FORMAT)

        self.uniq_id = "%s:%s" % (self.patient_id, mktime(self.arrived.timetuple()))
    
    @staticmethod
    def get_locations_at(store, qry_date):
        """! 
            get locations of patients at date_str
            @param store Store.Store: the store to get the data from
            @param qry_date datetime.datetime: the date and time at which we want to look
        """
        
        q_date_string = qry_date.strftime(TIME_FORMAT)
        
        qry = store.create_query()
        qry.mapkey_range=['', q_date_string]
        
        keys= []

        for l_res in store.get_view('Location_by_start_date',query=qry, dev=True):
            if l_res.value is None or l_res.value  > q_date_string :
                keys.append(l_res.docid)

        return store.fetch_objects(keys)

    @staticmethod
    def get_locations_between(store, from_date, to_date):
        """!
            get locations of patients at date_str
            
            TODO: Needs to be update to be store agnostic
            
            @param store Store.Store: the store to get the data from
            @param qry_date datetime.datetime: the date and time at which we want to look
        """

        #q_date_string = from_date.strftime(TIME_FORMAT)
        #q_end_string = to_date.strftime(TIME_FORMAT)

        #qry = store.create_query()
        #qry.mapkey_range=['', q_end_string] #we're using start date so it has to be before the end date.
        #qry.inclusive_end=True
        
        #keys= []
        #objs= []

        #for l_res in store.get_view('Location_by_start_date',query=qry, dev=True):
            #if l_res.value is None or l_res.value > q_date_string :
                #keys.append(l_res.docid)
                
        #if len(keys) > 0:
            #objs = store.fetch_objects(keys)
        
        store.get(Location, { 'op' : 'gt', 'value' : from_date }, { 'op' : 'lt', 'value' : to_date })
        
        return objs

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
    ## Patient's home postcode
    postcode = None
    ## List of associated hospital Numbers
    hospitalNumbers = []
    
    def __init__(self):
        uniq_id = ''
        nhs_number = ''
        sex = ''
        date_of_birth = None
        postcode = None
        hospitalNumbers = []
    
    def get_key_field(self):
        return 'nhs_number'
    
    ### return the anonymised unique identifier of the Patient
    def get_key(self):
        return self.uniq_id
     
    def from_dict(self, _dict, _map = None):
        super(Patient, self).from_dict(_dict, _map)
        
        if type(self.date_of_birth) == unicode or type(self.date_of_birth) == str:
            self.date_of_birth = datetime.datetime.strptime(self.date_of_birth, TIME_FORMAT)
        
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
    hash = None
    patient_id = None
    
    def get_key(self):
        return '%s:%s:%s' % (self.isolate_id, self.test_type, self.test_date.strftime('%Y-%m-%d'))
    
    def get_hash(self):
        import md5
        from json import dumps
        if self.result_type == 'Antibiogram' and self.result is not None:
            m = md5.new()
            m.update(dumps([ {ab['Antibiotic'] : ab['SIR'] for ab in self.result } ]))
            return str(m.hexdigest())
            

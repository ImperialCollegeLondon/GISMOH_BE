
#from plop.collector import Collector
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import parse_command_line, parse_config_file, define, options

import json
from os import path
import uuid
import datetime

from sec.basic import require_basic_auth
from sec import ldapauth

from store.SQL import SQLiteStore, MSSQLStore
from store.Couchbase import CouchbaseStore
from store import Store
from modules.Antibiogram import Antibiogram
from modules.Location import LocationInterface
from modules.Logging import *

define('port', default='8800')
define('debug', default=False)
define('db_type')
define('db_constr')
define('time_format', default='%Y-%m-%dT%H:%M:%S')
define('profile_out', default='profile.out')

def get_arg_or_default(torn, argname, default):
    try:
        arg = torn.get_argument(argname)
    except (tornado.web.MissingArgumentError):
        arg = default
    return arg

def create_db_instance():
    dbs = {
        'SQLITE' : SQLiteStore,
        'MSSQL' : MSSQLStore,
        'CB' : CouchbaseStore
    }
    cls = dbs[options.db_type]

    _map = Store.Mapping()

    _map.add_object('Patient', 'Patient', {
        'uniq_id': 'patient_id',
        'nhs_number' : 'nhsNumber',
        'sex' : 'sex',
        'date_of_birth' : 'dob',
        'postcode' : 'postcode'
    })

    return cls(options.db_constr, _map)
    

##Index page handler
#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('main.html')#,test_val=rowout)
        
#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class Antibiogram_Test(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        
        try:
            patient_id = float(get_arg_or_default(self,'patient_id', 1))
            at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime(options.time_format)), options.time_format)

            isolate_id = float(get_arg_or_default(self,'isolate_id', -1))
            
            _store = create_db_instance()
            #instance of the antibiogram module
            _abm = Antibiogram(_store)
            
            if isolate_id == -1 :
                _abs = _store.get_from_view_by_key('Results', patient_id)
    
    
                f_list = []
                p_list = []
    
                ab_list = _store.fetch(list(set([ unicode(obj.docid) for obj in _abs ])))
            else:
                ab_list = [Store.Result.get_by_key(isolate_id)]
        
            print ab_list
        
            for abx in ab_list.values() :
                for ab in _abm.get_nearest(abx.value, None, 11.5/12.0, gap_penalty = 0.25):
                    if not p_list.__contains__(ab['Result']['patient_id']) and ab['Result']['test_date'] <= at_date.strftime(options.time_format) and ab['Result']['patient_id'] != patient_id:
                        f_list.append(ab)
                        p_list.append(ab['Result']['patient_id'])


            self.add_header('Content-type', 'application/json')
        except:
          f_list = []
          print 'error'

        self.finish(json.dumps(f_list))

#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class Locations(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):

        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        self.add_header('Content-type', 'application/json')
        
        from_date =  datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)
        to_date =  datetime.datetime.strptime(get_arg_or_default(self,'to', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)
        
        _store = create_db_instance()
        
        locs = Store.Location.get_locations_between(_store, from_date, to_date)
        loc_list = [loc.get_dict() for loc in sorted( locs, key = lambda obj : obj.patient_id)  if loc.ward == 'SCBU' ]
        
        self.finish(json.dumps(loc_list))

#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class Isolates(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):

        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        self.add_header('Content-type', 'application/json')

        from_date =  datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)
        to_date =  datetime.datetime.strptime(get_arg_or_default(self,'to', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)

        _store = create_db_instance()
        isos = Store.Isolate.get_isolates_taken_between(_store, from_date, to_date)

        iso_list = [iso.get_dict() for iso in isos]

        self.finish(json.dumps(iso_list))

#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class OverlapHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        self.add_header('Content-type', 'application/json')
        
        patient_id = get_arg_or_default(self,'patient_id', False)
        date_from = datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)),options.time_format)
        date_to = datetime.datetime.strptime(get_arg_or_default(self,'to', datetime.datetime.now().strftime(options.time_format)), options.time_format)
        
        if patient_id == False :
            out_obj = []

        else:
            _store = create_db_instance()
            
            patient = _store.get(Store.Patient, patient_id)
            _loc_if = LocationInterface(_store)
        
            olaps = _loc_if.get_overlaps_with_patient(patient)
            olap_list = []
            
            for k in olaps:
                olap_list += [o.get_dict() for o in olaps[k]]
                
            out_obj = sorted(olap_list, key= lambda obj : obj['patient_id'])

        self.finish(json.dumps(out_obj))


#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class RiskAndPositiveHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        _store = create_db_instance()
        
        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime(options.time_format)), options.time_format)
        
        patients = {}
        
        for loc in Store.Location.get_locations_between(_store, at_date, at_date - datetime.timedelta(days=1)):
            pat = { 'patient_id' : loc.patient_id, 'location' : loc.get_dict(), 'admission' : Store.Admission.get_by_key(_store, loc.admission_id).get_dict() }
            patients[str(loc.patient_id)] = pat
            
        qry = _store.create_query()
        res = _store.get_view('Results', query=qry)

        result_keys = [ obj.docid for obj in res ]
        results = _store.fetch_objects(result_keys)

        iso_keys = [ u'Isolate:%s' % obj.isolate_id for obj in results ]
        _isolates = _store.fetch_objects(iso_keys)
        isolates = {}
        for _iso in _isolates:
            isolates[_iso.lab_number] = _iso

        for res in results:
         
            iso = isolates[res.isolate_id]
            
            #filter out future isolates if we're using the replay functionality
            if iso.date_taken > at_date or not res.result:
                continue
            
            if patients.has_key(str(iso.patient_id)):
                str_taken = iso.date_taken.strftime(options.time_format)
                patients[str(iso.patient_id)]['ab'] = res.get_dict()
                patients[str(iso.patient_id)]['type'] = 'positive' if str_taken > patients[str(iso.patient_id)]['admission']['start_date'] and str_taken < patients[str(iso.patient_id)]['admission']['end_date'] else 'risk'
                
        self.add_header('Content-type', 'application/json')
        self.finish(json.dumps([pat for pat in sorted(patients.values(), key = lambda obj : obj['patient_id']) if pat.has_key('ab') ]))


if __name__ == "__main__":
    parse_config_file('./GISMOH.conf')
    parse_command_line(final=True)

    logger = get_logger(__name__)
    add_file_handler(logger)

    settings = dict(
       template_path = path.join(path.dirname(__file__), "templates"),
       static_path = path.join(path.dirname(__file__), "static"),
       debug = options.debug
    )

    application = tornado.web.Application([
        (r'/api/antibiogram', Antibiogram_Test),
        (r'/api/overlaps', OverlapHandler),
        (r'/api/locations', Locations),
        (r'/api/isolates', Isolates),
        (r'/api/risk_patients', RiskAndPositiveHandler),
        (r"/", MainHandler)
    ], **settings)

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

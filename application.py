import tornado.ioloop
import tornado.web

import json
from os import path
import uuid
import datetime

from sec.basic import require_basic_auth
from sec import ldapauth

from store import Store
from modules.Antibiogram import Antibiogram

print 'started'

def get_arg_or_default(torn, argname, default):
    try:
        arg = torn.get_argument(argname)
    except (tornado.web.MissingArgumentError):
        arg = default
    return arg

##Index page handler
@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('main.html')#,test_val=rowout)
        
@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class Antibiogram_Test(tornado.web.RequestHandler):
    def get(self):
        
        iso_id = float(get_arg_or_default(self,'isolate_id', 1.0))

        _store = Store.Store('GISMOH', 'gismoh2')
  
        _abm = Antibiogram(_store)
        
        abs = _store.get_from_view_by_key('Results', iso_id)
        
        aaaaa = []
        ab_list = []
        
        for ab_i in abs :
            
            ab = _store.fetch(ab_i.docid).value

            ab_list = ab_list + [x['Antibiotic'] for x in ab['result']]
            
            aaaaa = _abm.get_nearest(ab, None, 11.5/12.0, gap_penalty = 0.25)
        
        self.add_header('Content-type', 'application/json')
        self.write(json.dumps(aaaaa))

@require_basic_auth('GISMOH', ldapauth.auth_user_ldap) 
class OverlapHandler(tornado.web.RequestHandler):
    def get(self):
        from modules.Location import LocationInterface
        import datetime
        
        patient_id = float(get_arg_or_default(self,'patient_id', 1.0))
        date_from = datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        date_to = datetime.datetime.strptime(get_arg_or_default(self,'to', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        
        _store = Store.Store('GISMOH', 'gismoh2')
        
        patient = Store.Patient.get_by_key(_store, patient_id)
        _loc_if = LocationInterface(_store)
    
        olaps = _loc_if.get_overlaps_with_patient(patient)
    
        for k in olaps:
            olaps[k] = [o.get_dict() for o in olaps[k]]
    
        self.add_header('Content-type', 'application/json')
        self.write(json.dumps(olaps))

@require_basic_auth('GISMOH', ldapauth.auth_user_ldap) 
class RiskAndPositiveHandler(tornado.web.RequestHandler):
    def get(self):

        _store = Store.Store('GISMOH', 'gismoh2')
        
        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        
        patients = {}
        
        for loc in Store.Location.get_locations_at(_store, at_date):
            pat = { 'patient_id' : loc.patient_id, 'location' : loc.get_dict() } #, 'admission' : Store.Admission.get_by_key(_store, loc.admission_id).get_dict() }
            patients[str(loc.patient_id)] = pat
            
        for res_res in _store.get_next_from('Results'):
            res = Store.Result.get_by_key(_store, res_res.docid)
            iso = Store.Isolate.get_by_key(_store, res.isolate_id)

            if patients.has_key(iso.patient_id):
                patients[str(iso.patient_id)]['ab'] = res.get_dict()
         
        self.add_header('Content-type', 'application/json')
        self.write(json.dumps(patients))   
            
        

settings = dict(
   template_path = path.join(path.dirname(__file__), "templates"),
   static_path = path.join(path.dirname(__file__), "static"),
   debug = True
)

application = tornado.web.Application([
    (r'/antibiogram', Antibiogram_Test),
    (r'/overlaps', OverlapHandler),
    (r'/risk_patients', RiskAndPositiveHandler),
    (r"/", MainHandler)
], **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
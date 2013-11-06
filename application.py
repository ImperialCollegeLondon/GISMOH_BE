import tornado.ioloop
import tornado.web
from tornado import gen

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
        
        patient_id = float(get_arg_or_default(self,'patient_id', 1))
        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        
        _store = Store.Store('GISMOH', 'gismoh2')
  
        _abm = Antibiogram(_store)
        
        abs = _store.get_from_view_by_key('Results', patient_id)
        
        f_list = []
        p_list = []
        
        for ab_i in abs :
            ab = _store.fetch(ab_i.docid).value
            for ab in _abm.get_nearest(ab, None, 11.5/12.0, gap_penalty = 0.25):
                if not p_list.__contains__(ab['Result']['patient_id']) and ab['Result']['test_date'] < at_date.strftime('%Y-%m-%d %H:%M:%S') and ab['Result']['patient_id'] != patient_id:
                    f_list.append(ab)
                    p_list.append(ab['Result']['patient_id'])
            
             
        self.add_header('Content-type', 'application/json')
        self.write(json.dumps(f_list))

@require_basic_auth('GISMOH', ldapauth.auth_user_ldap) 
class OverlapHandler(tornado.web.RequestHandler):
    def get(self):
        from modules.Location import LocationInterface
        import datetime
        
        self.add_header('Content-type', 'application/json')
        
        patient_id = float(get_arg_or_default(self,'patient_id', 0.0))
        date_from = datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        date_to = datetime.datetime.strptime(get_arg_or_default(self,'to', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        
        if patient_id == 0.0 :
            self.write('[]')
        else:
            _store = Store.Store('GISMOH', 'gismoh2')
            
            patient = Store.Patient.get_by_key(_store, patient_id)
            _loc_if = LocationInterface(_store)
        
            olaps = _loc_if.get_overlaps_with_patient(patient)
            olap_list = []
            
            for k in olaps:
                olap_list += [o.get_dict() for o in olaps[k]]
        
            
            self.write(json.dumps(olap_list))

@require_basic_auth('GISMOH', ldapauth.auth_user_ldap) 
class RiskAndPositiveHandler(tornado.web.RequestHandler):
    def get(self):

        _store = Store.Store('GISMOH', 'gismoh2')
        
        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
        
        patients = {}
        
        for loc in Store.Location.get_locations_at(_store, at_date):
            pat = { 'patient_id' : loc.patient_id, 'location' : loc.get_dict(), 'admission' : Store.Admission.get_by_key(_store, loc.admission_id).get_dict() }
            patients[str(loc.patient_id)] = pat
            
        qry = _store.create_query()
        #qry.mapkey_multi = [[key] for key in patients.keys()] 
        res = _store.get_view('Results', query=qry)
        for res_res in res:
         
            res = Store.Result.get_by_key(_store, res_res.docid)
            iso = Store.Isolate.get_by_key(_store, res.isolate_id)
            
            if iso.date_taken > at_date.strftime('%Y-%m-%d %H:%M:%S') or not res.result:
                
                continue
            
            if patients.has_key(str(iso.patient_id)):
                str_taken = iso.date_taken
                patients[str(iso.patient_id)]['ab'] = res.get_dict()
                patients[str(iso.patient_id)]['type'] = 'positive' if str_taken > patients[str(iso.patient_id)]['admission']['start_date'] and str_taken < patients[str(iso.patient_id)]['admission']['end_date'] else 'risk'
                
        self.add_header('Content-type', 'application/json')
        self.write(json.dumps([pat for pat in sorted(patients.values(), key = lambda obj : obj['patient_id']) if pat.has_key('ab') ]))   
            
        

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
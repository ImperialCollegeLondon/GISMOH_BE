#! /usr/bin/env python

# 12/05/2014 begin modifications to backend serve

import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import parse_command_line, parse_config_file, define, options
import json
from os import path
import uuid
import datetime


from store.SQL import SQLiteStore, MSSQLStore
from store import Store
from modules.Antibiogram import Antibiogram
from modules.Location import LocationInterface
from modules.Logging import *
from modules.analysis.Base import AnalysisRequest, AnalysisNotificationReciever

#define configuration options for GISMOH
define('port', default='3000')
define('debug', default=True)
define('db_type')
define('db_constr')
define('time_format', default='%Y-%m-%dT%H:%M:%S')
define('profile_out', default='profile.out')
define('rabbit_server', default='192.168.30.10')
define('rabbit_port', default=5672)
define('analysis_request_exchange', default='analysis')
define('analysis_notification_exchange', default='analysis.notifications')
define('similarity_queue', default='analysis.similarity')
define('rabbit_prefix', default='gismoh')

#helper method to return a HTTP GET argument or a default value
def get_arg_or_default(torn, argname, default):
    try:
        arg = torn.get_argument(argname)
    except (tornado.web.MissingArgumentError):
        arg = default
    return arg

#Create and return and instance of a database connection
def create_db_instance(db_type = None, con_str = None):
    if db_type is None:
        db_type = options.db_type
    if con_str is None:
        con_str = options.db_constr

    dbs = {
        'SQLITE' : SQLiteStore,
        'MSSQL' : MSSQLStore
    }
    cls = dbs[db_type]

    #Mapping for this database... should be moved into a settings file
    _map = Store.Mapping()

    _map.add_object('Patient', 'Patient', {
        'uniq_id': 'patient_id',
        'nhs_number' : 'nhsNumber',
        'sex' : 'sex',
        'date_of_birth' : 'dob',
        'postcode' : 'postcode'
    })

    _map.add_object('PatientHospitalNumber', 'PatientHospitalNumber', {
        'patient_id': 'patient_id',
        'hospital' : 'hospital_id',
        'hospital_number' : 'hospitalNumber'
    })

    _map.add_object('Location', 'PatientLocation',{
        'uniq_id' : 'pl_id',
        'ward' : 'ward_id',
        'specialty': 'speciality',
        'arrived' : 'date_arrived',
        'left' : 'date_left',
        'patient_id' : 'patient_id'
    })

    _map.add_object('Isolate', 'Isolate',{
        'lab_number' : 'isolate_id',
        'patient_id' : 'patient_id',
        'date_taken' : 'taken',
        'organism' : 'organism',
        'location': 'location',
        'sample_site' : 'sample_site',
        'meta_data' : 'meta_data'
    })

    _map.add_object('Antibiogram', 'Antibiogram', {
        'instance_id' : 'instance_id',
        'isolate_id' : 'isolate_id',
        'organism' : 'organism',
        'sir_results' : 'sir_results',
        'sir_result_identifier' : 'sir_results_identifier',
        'zone_size_results' : 'zone_size_results',
        'is_resistant' : 'resistant',
        'print_number' : 'print_number',
        'date_tested' : 'test_date',
    })

    _map.add_object('Ward', 'Ward', {
        'uniq_id' : 'ward_id',
        'shortName': 'shortName',
        'fullName' : 'fullName',
        'n_beds' : 'n_beds',
        'hospital_id' : 'hospital_id',
        'include' : 'include'
    })

    return cls(con_str, _map)


##Index page handler
#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('main.html')#,test_val=rowout)

## Handle Antibiogram data requests
#   For a given isolate of a given patient, return all Antibiogram links before a certain date.
#   Uses the Antibiogram module to determine isolate similarity
#
# Args:
#   patient_id : The GISMOH Internal ID of the paitent (as opposed to NHS Number)
#   at_date : The current date or date we are interested in
#   isolate : The Isolate we want to base our investigation on
#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class AntibiogramHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")


        patient_id = float(get_arg_or_default(self,'patient_id', 1))
        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime(options.time_format)), options.time_format)

        isolate_id = get_arg_or_default(self,'isolate_id', -1)

        _store = create_db_instance(options.db_type, options.db_constr)
        #instance of the antibiogram module


        p_list = []
        f_list= []

        # Isolate ID can be 0 so -1 is the "no isolate" value
        if isolate_id != -1 :
            #ref_iso : reference isolate : the isolate we are comparing to.
            ref_iso = Store.Isolate.get(_store, isolate_id)

            # get all antibiograms for this isolate.
            ab_list = Antibiogram.get_by(_store, 'isolate_id', isolate_id)

            for abx in ab_list :
                for ab in Antibiogram.get_nearest(_store, abx, None, 11.5/12.0, gap_penalty = 0.25):
                    isolate = Store.Isolate.get(_store, ab['Antibiogram'].isolate_id)
                    patient = Store.Patient.get(_store, isolate.patient_id)

                    patnum = patient.nhs_number

                    if patnum is None or patnum == '':
                        patnums = Store.PatientHospitalNumber.get_by(_store, 'patient_id', patient.uniq_id)

                        if len(patnums) > 0:
                            patnum = patnums[0].hospital_number

                    if isolate.patient_id not in p_list and isolate.date_taken <= at_date and isolate.patient_id != ref_iso.patient_id:
                        i_dic = isolate.get_dict(True)
                        i_dic['patient_number'] = patnum

                        ab['Antibiogram'] = ab['Antibiogram'].get_dict(True)
                        ab['Isolate'] = i_dic
                        f_list.append(ab)
                        p_list.append(isolate.patient_id)

        self.add_header('Content-type', 'application/json')
        self.finish(json.dumps(f_list))

# Use the Location interface to return a JSON object of tall Patient locations between
# from_date and to_date
class Locations(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):

        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        self.add_header('Content-type', 'application/json')

        from_date =  datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)
        to_date =  datetime.datetime.strptime(get_arg_or_default(self,'to', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)

        _store = create_db_instance(options.db_type, options.db_constr)

        loc_list= []

        locs = Store.Location.get_locations_between(_store, from_date, to_date)
        for loc in locs:
            pnum = Store.Patient.get(_store, loc.patient_id).nhs_number
            if pnum is None or pnum == '':
                pns = Store.PatientHospitalNumber.get_by(_store, 'patient_id', loc.patient_id)
                pnum = pns[0].hospital_number

            ld = loc.get_dict(True)
            ld['patient_number'] = pnum
            ld['ward_name'] = Store.Ward.get(_store, loc.ward).shortName

            loc_list.append(ld)


        self.finish(json.dumps(loc_list))

# Return a JSON object of all Isolates between from_date and to_date
class Isolates(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):

        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        self.add_header('Content-type', 'application/json')

        from_date =  datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)
        to_date =  datetime.datetime.strptime(get_arg_or_default(self,'to', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)), options.time_format)

        _store = create_db_instance(options.db_type, options.db_constr)
        isos = Store.Isolate.get_isolates_taken_between(_store, from_date, to_date)

        for iso in isos:
            iso.result = [ab.get_dict(True) for ab in Antibiogram.get_by(_store, 'isolate_id', iso.lab_number) ]


        self.finish(json.dumps([i.get_dict(True) for i in isos]))

# Return a JSON object with details of locations that overlapped with a patient (patient_id)
# between the dates from and to
class OverlapHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
       #allow connections from grunt-connect-proxy
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        # set the type of the response to json
        self.add_header('Content-type', 'application/json')

        #the patient that has been selected
        patient_id = get_arg_or_default(self,'patient_id', False)
        #the start date of the range (get param = 'from')
        date_from = datetime.datetime.strptime(get_arg_or_default(self,'from', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(options.time_format)),options.time_format)
        #the end date of the range (get param = 'to')
        date_to = datetime.datetime.strptime(get_arg_or_default(self,'to', datetime.datetime.now().strftime(options.time_format)), options.time_format)

        #if the patient wasn't specified we can short-cut everything as we know there won't be any overlaps
        if patient_id == False :
            out_obj = []

        else:
            #connect to the database
            _store = create_db_instance(options.db_type, options.db_constr)

            #get the patient object
            patient = _store.get(Store.Patient, patient_id)

            #get the location interface (from modules.location)
            _loc_if = LocationInterface(_store)

            #get this list of overlaps
            olaps = _loc_if.get_overlaps_with_patient(patient)

            #conver the list of Patient Location objects into dictionaries so they can be JSON serialized
            olap_list = []

            for k in olaps:
                olap_list += [o.get_dict(True) for o in olaps[k]]

            out_obj = sorted(olap_list, key= lambda obj : obj['patient_id'])

        #dump the JSON representation of the overlaps list out to the response
        self.finish(json.dumps(out_obj))


#@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class RiskAndPositiveHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")
        _store = create_db_instance(options.db_type, options.db_constr)

        interval = get_arg_or_default(self, 'days' , 1)

        at_date = datetime.datetime.strptime(get_arg_or_default(self,'at_date', datetime.datetime.now().strftime(options.time_format)), options.time_format)
        cutoff_date = at_date - datetime.timedelta(days = interval)

        patients = {}

        for loc in Store.Location.get_locations_between(_store, at_date, at_date - datetime.timedelta(days=1)):
            patient = Store.Patient.get(_store, loc.patient_id)

            if patient.nhs_number is None or patient.nhs_number == '':
                pns = Store.PatientHospitalNumber.get_by(_store, 'patient_id', loc.patient_id)
                if len(pns) > 0:
                    pnum = pns[0].hospital_number
                else:
                    pnum = 'No ID'
            else:
                pnum = patient.nhs_number

            loc.ward_name = Store.Ward.get(_store, loc.ward).shortName

            pat = { 'patient_id' : loc.patient_id, 'patient_number' : pnum, 'location' : loc.get_dict(True)}
            patients[str(loc.patient_id)] = pat

        if len(patients.keys()) > 0:
            isolates = _store.find(Store.Isolate, { 'field' : 'date_taken', 'op' : '>', 'value' : cutoff_date })
        else :
            isolates = []

        for iso in isolates:
            results = Antibiogram.get_by(_store, 'isolate_id', iso.lab_number)

            res = results[0]

            #filter out future isolates if we're using the replay functionality
            if iso.date_taken > at_date:
                continue

            if patients.has_key(str(iso.patient_id)):
                str_taken = iso.date_taken.strftime(options.time_format)
                patients[str(iso.patient_id)]['ab'] = res.get_dict(True)
                patients[str(iso.patient_id)]['type'] = 'positive' if res.is_resistant else 'risk'

        self.add_header('Content-type', 'application/json')
        self.finish(json.dumps([pat for pat in sorted(patients.values(), key = lambda obj : obj['patient_id']) if pat.has_key('ab') ]))

class SimiliarityAnalysisDispatchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:9000")

        isolate_ids = get_arg_or_default(self, 'isolate_id', '').split(',')

        analysis_request = AnalysisRequest('similarity', isolate_ids)

        request_uuid = analysis_request.start_request()

        self.listener = AnalysisNotificationReciever('similarity', request_uuid, self.on_result_recieved)

    def on_result_recieved(self, message_id, app_id, body):
        self.listener.acknowledge(message_id)
        self.write(body)

        self.listener.close()
        self.finish()




def rabbit_error(*args):
    print '---- %s' % args

def request_similarity_analysis(isolate_ids):
    analysis_request('similarity', { 'isolate_ids' : isolate_ids })

def check_for_response(type, uuid):
    pass

def wait_for_response(type, uuid, callback):
    pass

def init_app():
    parse_config_file('./GISMOH.conf')
    parse_command_line(final=True)

    settings = dict(
       template_path = path.join(path.dirname(__file__), "templates"),
       static_path = path.join(path.dirname(__file__), "static"),
       debug = options.debug
    )

    application = tornado.web.Application([
        (r'/api/antibiogram', AntibiogramHandler),
        (r'/api/overlaps', OverlapHandler),
        (r'/api/locations', Locations),
        (r'/api/isolates', Isolates),
        (r'/api/risk_patients', RiskAndPositiveHandler),
        (r'/api/similarity', SimiliarityAnalysisDispatchHandler),
        (r"/", MainHandler)
    ], **settings)

    return application

if __name__ == "__main__":
    application = init_app()

    logger = get_logger(__name__)
    add_file_handler(logger)
    add_console_handler(logger)

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

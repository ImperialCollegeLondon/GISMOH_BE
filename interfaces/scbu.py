import store.Store as Store
import xlrd
import datetime
from time import mktime
from re import match
import uuid

from interfaces.Rabbit import Connection
from modules.ObjectMessaging import ObjectSender
from modules.Antibiogram import Antibiogram

from tornado.options import options
from application import init_app

from modules import Logging

logger = Logging.get_logger('SCBU Importer')
Logging.add_console_handler(logger)

rabbit_logging = Logging.get_logger('pika')
Logging.set_level(rabbit_logging, 'error')

##Import data from the SCBU dataset
class SCBU_Importer(object):
    reader = None
    sender = None

    def __init__(self, filename, connection):
        self.reader = xlrd.open_workbook(filename)
        self.sender = ObjectSender(connection)

    def read_admissions(self):
        _rr = self.row_reader('Admissions')

        headers = _rr.next();
        self.adm = Store.Admission()

        curlocs = []

        for row in _rr:
            logger.info(row)
            patient = self.read_patient(row, headers)
            location = self.read_location(row, headers)

            if self.adm.patient_id is not None and (self.adm.patient_id != patient.uniq_id or location.arrived != prev.left):

                for l in curlocs:
                    l.admission_id = self.adm.get_key()
                    #self.sender.send(l)
                curlocs = []

                #self.sender.send(self.adm)

                self.adm = Store.Admission()

            if self.adm.patient_id is None:
                self.adm.patient_id = patient.uniq_id

            if self.adm.start_date is None or self.adm.start_date > location.arrived:
                self.adm.start_date = location.arrived

            if self.adm.end_date is None or self.adm.end_date < location.left:
                self.adm.end_date = location.left

            curlocs.append(location)
            prev = location

    def read_isolates(self):
        _rr = self.row_reader('Microbiology')

        headers = _rr.next()

        for row in _rr:
            isolate = self.read_isolate(row, headers)

    def row_reader(self, sheetname):
        sheet = self.reader.sheet_by_name(sheetname)

        for i in range(sheet.nrows):
            data = sheet.row_values(i)
            types = sheet.row_types(i)

            result = []

            for j in range(len(data)):
                if types[j] == xlrd.XL_CELL_DATE :
                    _tuple = xlrd.xldate_as_tuple(data[j], self.reader.datemode)
                    result.append(datetime.datetime(_tuple[0], _tuple[1], _tuple[2], _tuple[3], _tuple[4], _tuple[5]))
                else:
                    result.append(data[j])

            yield result

    def read_patient(self, row, headers):
        _dict = dict(zip(headers, row))

        _pat = Store.Patient()
        _pat.from_dict(_dict, {
            'Patient_Number' : 'nhs_number'
        })
        self.sender.send(_pat)
        return _pat

    def read_location(self, row, headers):
        _dict = dict(zip(headers, row))

        _location = Store.Location()

        _location.from_dict(_dict,{
            'Patient_Number' : 'nhs_number',
            'EpisodeAdmissionDate' : 'arrived',
            'EpisodeDischargeDate' : 'left',
            'Ward' : 'ward'
        })
        _location.speciality = 'Pediatrics'

        return _location


    def read_isolate(self, row, headers):
        _dict = dict(zip(headers, row))

        _iso = Store.Isolate()
        _iso.from_dict(_dict, {
            'Patient_Number': 'nhs_number',
            'Isolate_Number': 'lab_number',
            'DateSent' : 'date_taken'
        })


        _iso.meta_tags = {
            'st' : _dict['ST'],
            'accession_number' : _dict['Accession_Number']
        }

        _result = Antibiogram()
        _result.isolate_id = _dict['Isolate_Number']
        _result.date_tested = _iso.date_taken
        _result.organism = 'Staphylcoccus aureus'


        ab_dict = {}

        for h in headers:
            if h.startswith('SR') and _dict[h] != '':
                abname = h.replace('SR', '')
                ab_dict[abname] = _dict[h]

        _result.sir_result = ab_dict
        _result.sir_results_identifier = _result.get_result_identifier()

        print _iso
        self.sender.send(_iso)
        self.sender.send(_result)

def start(connection):
    global importer
    logger.info('start...')
    importer = SCBU_Importer(options.file, connection)
    importer.sender.onReady = run

def run():
    global importer
    logger.info('run..')
    importer.read_admissions()
    importer.read_isolates()

def end():
    connection.close()

if __name__ == '__main__':
    init_app()
    rabbit_connection = Connection(options.rabbit_server)
    rabbit_connection.addOnReady(start)
    logger.info('running io...')
    rabbit_connection.runio()

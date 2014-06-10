import store.Store as Store
import xlrd
import datetime
from time import mktime
from re import match
import uuid

##Import data from the SCBU dataset
class SCBU_Importer(object):
    reader = None
    sender = None

    def __init__(self, filename, store):
        self.reader = xlrd.open_workbook(filename)
        self.sender = ObjectSender()

    def read_admissions(self):
        _rr = self.row_reader('Admissions')

        headers = _rr.next();
        self.adm = Store.Admission()

        curlocs = []

        for row in _rr:
            #print row
            patient = self.read_patient(row, headers)
            location = self.read_location(row, headers)

            if self.adm.patient_id is not None and (self.adm.patient_id != patient.uniq_id or location.arrived != prev.left):

                for l in curlocs:
                    l.admission_id = self.adm.get_key()
                    self.store.save(l)
                curlocs = []

                self.store.save(self.adm)

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
            'Patient_Number' : 'uniq_id'
        })
        self.store.save(_pat)
        return _pat

    def read_location(self, row, headers):
        _dict = dict(zip(headers, row))

        _location = Store.Location()

        _location.from_dict(_dict,{
            'Patient_Number' : 'patient_id',
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
            'Patient_Number': 'patient_id',
            'Isolate_Number': 'lab_number',
            'DateSent' : 'date_taken'
        })


        _iso.meta_tags = {
            'st' : _dict['ST'],
            'accession_number' : _dict['Accession_Number']
        }

        _result = Store.Result()
        _result.test_type = 'Disc Diffusion'
        _result.result_type = 'Antibiogram'
        _result.isolate_id = _dict['Isolate_Number']
        _result.test_date = _iso.date_taken
        _result.result = []
        _result.patient_id = _dict['Patient_Number']

        str_ab = ''

        for h in headers:
            if h.startswith('SR') and _dict[h] != '':
                abname = h.replace('SR', '')

                ab_dict = {
                    'Antibiotic' : abname,
                    'SIR' : _dict[h]
                }

                str_ab += _dict[h]

                _result.result.append(ab_dict)


        self.store.save(_iso)
        self.store.save(_result)

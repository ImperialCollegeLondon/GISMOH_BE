import csv

from store.Store import Patient, Isolate
from modules.Antibiogram import Antibiogram, AntibiogramIdentifier
from datetime import datetime

from tornado.options import options

from modules.ObjectMessaging import ObjectSender
from interfaces.rabbit import Connection

import os

class MeditechImport:
    store = None
    sender = None
    rabbit_connection = None

    def __init__(self, store, directory):
        self.store = store
        self.directory = directory
        self.rabbit_connection = Connection(options.rabbit_server)
        self.sender = ObjectSender(self.rabbit_connection)

        self.iso = None
        self.ab = None

    def open_file(self, filename):
        self.fp = open(filename)
        self.reader = csv.DictReader(self.fp, delimiter=';', quotechar = '"')


    def read_line(self, row_dict):
        patient = None
        if self.iso is None or self.iso.lab_number != row_dict['Specimen No']:

            patient = Patient.get_by_hospital_number(self.store, 'ADD', row_dict['Unit Number'])
            if patient is None:
                patient = Patient()
                patient.date_of_birth = datetime.strptime(row_dict['DOB'], '%d/%m/%Y') if row_dict['DOB'] != '' else None
                patient.sex = row_dict['Sex']

                patient.add_hospital_number('ADD', row_dict['Unit Number'])

                self.sender.send(patient)


            if self.iso and self.iso.lab_number != row_dict['Specimen No']:
                #self.ab.save(self.store)
                self.sender.send(self.ab)
                self.iso = Isolate.get(self.store, row_dict['Specimen No'])

            if self.iso is None:
                self.iso = Isolate()
                self.iso.patient_id = patient.uniq_id
                self.iso.lab_number = row_dict['Specimen No']
                self.iso.date_taken = datetime.strptime(row_dict['Date Received'], '%Y-%m-%d %H:%M:%S')
                self.iso.organism = row_dict['Organism']
                self.iso.sample_site = row_dict['Sample']
                self.iso.location = row_dict['Location']
                self.iso.meta_data['Test'] = row_dict['Test']
                self.iso.meta_data['GP'] = row_dict['GP']
                self.iso.meta_data['Consultant'] = row_dict['Consultant']

                self.sender.send(self.iso)

            test_date =  datetime.strptime(row_dict['Date tested'], '%Y-%m-%d %H:%M:%S')

            self.ab = Antibiogram.find(self.store, self.iso.lab_number, test_date)
            if self.ab == None:
                self.ab = Antibiogram()
                self.ab.isolate_id = self.iso.lab_number
                self.ab.organism = self.iso.organism
                self.ab.date_tested = test_date
                self.ab.print_number = row_dict['Print No.']

        self.ab.sir_results[row_dict['Antibiotic']] = row_dict['Result']
        self.ab.zone_size_results[row_dict['Antibiotic']] = row_dict['Zone Size']


    def read_file(self, ofn):

        if ofn.startswith('.'):
            return

        filename = '%s/%s' % (self.directory, ofn)

        nfn = '%s/gmi_%s' % (self.directory, ofn)

        #os.rename(filename, nfn)

        self.open_file(filename)
        for row in self.reader:
            self.read_line(row)

        self.sender.send(self.ab)

    def scan_dir(self):
        import os, time

        for f in os.listdir(self.directory):
            if not f.startswith('gmi_'):
                self.read_file(f)


if __name__ == "__main__":
    from tornado.options import parse_command_line, parse_config_file, define, options
    from application import create_db_instance

    define('dir')

    parse_config_file('./GISMOH.conf')
    parse_command_line(final=True)


    importer = MeditechImport(create_db_instance(options.db_type, options.db_constr), options.dir)
    importer.scan_dir()

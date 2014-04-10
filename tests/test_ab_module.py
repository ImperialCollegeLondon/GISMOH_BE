from nose.tools import raises, with_setup
import datetime
import unittest
import json

from modules.Antibiogram import Antibiogram, AntibiogramInterface

class AntibiogramModuleTester(unittest.TestCase):
    def test_identifier(self):
        ab1 = Antibiogram()
        
        ab1.sir_results = {
            "Ciprofloxacin" : "R",
            "Flucloxacilin" : "S"
        }
        
        ab2 = Antibiogram()
        
        ab2.sir_results = {
            "Flucloxacilin" : "S",
            "Ciprofloxacin" : "R"
        }
        
        ab3 = Antibiogram()
        
        ab3.sir_results = {
            "Flucloxacilin" : "R",
            "Ciprofloxacin" : "R"
        }
        
        assert ab1.get_result_identifier() == ab2.get_result_identifier()
        assert ab1.get_result_identifier() != ab3.get_result_identifier()
        
    def test_identifier_assignment(self):
        ab1 = Antibiogram()
        
        ab1.sir_results = {
            "Ciprofloxacin" : "R",
            "Flucloxacilin" : "S"
        }
        
        ab1_d = ab1.get_dict()
        
        assert ab1_d['sir_result_identifier'] == ab1.get_result_identifier()
        assert type(ab1_d['sir_results']) == str
        assert ab1_d['sir_results'] == json.dumps(ab1.sir_results)
        
    